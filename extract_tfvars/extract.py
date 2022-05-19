# TODO: Given a module do the following:
# DONE: 1) Given a project name create a folder
# DONE: 2) Download variables.tf file into the local repo
# TODO: 3) Extract variable names into try syntax and create the module main.tf file
# TODO: 4) Populate folder structure if required
# TODO: Add unit tests
import re, os, urllib.request

var_pattern = re.compile('(?<=variable\s").*(?="\s{)')

# User inputs
project_name = input("Project name: ")
module_github_project_name = input("Module Github Project Name: ")

service_name = re.sub("terraform-aws-", "", module_github_project_name)
print(service_name)

cwd = os.getcwd()
# Make folder for the project
if os.path.isdir(f"{cwd}/{project_name}"):
    print("Folder already exists, moving on..")
else:
    os.mkdir(project_name)

raw_var_url = f"https://raw.githubusercontent.com/terraform-aws-modules/{module_github_project_name}/master/variables.tf"
var_file_name = f"{cwd}/{project_name}/{service_name}_variables.tf"
    
filename, headers = urllib.request.urlretrieve(raw_var_url, filename=var_file_name)

tfvars = open(var_file_name, "r")

result = re.findall(var_pattern, tfvars.read())

f = open(f"{cwd}/{project_name}/{service_name}.tf", "a")

f.write(f"""
            module "{service_name}" {{
            source  = "terraform-aws-modules/{service_name}/aws"
            version = "~> <INSERT_VERSION>"
            
        """)

for var in result:
    if "tag" not in var:
        f.write(f"{var} = try(each.value.{var}, var.{var})\n")
    elif "tag" in var:
        f.write(f"{var} = merge(try(each.value.{var}, var.{var}, {{}}), local.default_tags)\n")

f.write("\n}")

f.close()

os.system(f"terraform fmt --recursive {cwd}/{project_name}/")