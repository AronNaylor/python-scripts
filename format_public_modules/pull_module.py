# TODO: Given a module do the following:
# DONE: 1) Given a project name create a folder
# DONE: 2) Download variables.tf file into the local repo
# DONE: 3) Extract variable names into try syntax and create the module main.tf file
# DONE: 4) Populate folder structure if required
# DONE: 5) Handle submodules
# TODO: SOrt out submodule path
# TODO: Add unit tests
import re, os, urllib.request

# User inputs
project_name = input("Project name: ")
is_submodule = input("Is the module you are requesting a sub module? ")

if is_submodule.lower() == "yes":
    module_github_submodule_project_name = input("Submodule project name in Github? ")
    module_github_parent_project_name = input("Module Github Parent Project Name (I.e, terraform-aws-vpc): ")
    module_version = input("Parent Module version required (I.e, v1.0.0): ")
else:
    module_github_project_name = input("Module Github Project Name: ")
    module_version = input("Module version required (I.e, v1.0.0): ")

def root_module():
    service_name = re.sub("terraform-aws-", "", module_github_project_name)
    raw_var_url = f"https://raw.githubusercontent.com/terraform-aws-modules/{module_github_project_name}/{module_version}/variables.tf"
    var_file_name = f"{cwd}/{project_name}/{service_name}_variables.tf"
    filename, headers = urllib.request.urlretrieve(raw_var_url, filename=var_file_name)
    tfvars = open(var_file_name, "r")
    result = re.findall(var_pattern, tfvars.read())
    f = open(f"{cwd}/{project_name}/{service_name}.tf", "a")
    f.write(f"""
                module "{service_name}" {{
                source  = "terraform-aws-modules/{service_name}/aws"
                version = "~> {module_version}"
                
            """)
    for var in result:
        if "tag" not in var:
            f.write(f"{var} = try(each.value.{var}, var.{var})\n")
        elif "tag" in var:
            f.write(f"{var} = merge(try(each.value.{var}, var.{var}, {{}}), local.default_tags)\n")
    f.write("\n}")
    f.close()
    
def sub_module():
    parent_service_name = re.sub("terraform-aws-", "", module_github_parent_project_name)
    raw_var_url = f"https://raw.githubusercontent.com/terraform-aws-modules/{module_github_parent_project_name}/{module_version}/modules/{module_github_submodule_project_name}/variables.tf"
    print(f"URL: {raw_var_url}")
    var_file_name = f"{cwd}/{project_name}/{module_github_submodule_project_name}_variables.tf"
    filename, headers = urllib.request.urlretrieve(raw_var_url, filename=var_file_name)
    tfvars = open(var_file_name, "r")
    result = re.findall(var_pattern, tfvars.read())
    f = open(f"{cwd}/{project_name}/{module_github_submodule_project_name}.tf", "a")
    f.write(f"""
                module "{module_github_submodule_project_name}" {{
                source  = "terraform-aws-modules/{parent_service_name}/aws//modules/{module_github_submodule_project_name}"
                version = "~> {module_version}"
                
            """)
    for var in result:
        if "tag" not in var:
            f.write(f"{var} = try(each.value.{var}, var.{var})\n")
        elif "tag" in var:
            f.write(f"{var} = merge(try(each.value.{var}, var.{var}, {{}}), local.default_tags)\n")
    f.write("\n}")
    f.close()

cwd = os.getcwd()
# Make folder for the project
if os.path.isdir(f"{cwd}/{project_name}"):
    print("Folder already exists, moving on..")
else:
    os.mkdir(project_name)
    
var_pattern = re.compile('(?<=variable\s").*(?="\s{)')
    
if is_submodule.lower() == "no":
    root_module()
elif is_submodule.lower() == "yes":
    sub_module()
    
os.system(f"terraform fmt --recursive {cwd}/{project_name}/")