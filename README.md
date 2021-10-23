# Automation Cloud Base Instance (EC2 AWS)
Create an automation that setups either a virtual machine or a cloud based instance and installs & configures a service into it. The service can be anything you want as long as it listens to network connections. Use an empty GIT repository and commit your code to it with proper commit messages.


Requirements
+ Launches a virtual machine or a cloud instance
+ operating system can be any Linux based distribution of your choicecan be a ready made base image from a public 3rd party

Provides two installation methods for the service

+ install the service from a released build (eg. deb/rpm package or tar.gz)
+ build from version control repository with defined branch and revision

Configures the service

+ modifies the behaviour of default installation

Includes tests that verify 

+ service has been installed
+ service is runniing
+ correct version / revision is being used - command line use
+ configuration changes are applied and correct
+ service listens to necessary ports

## Оглавление

0. [Description](#Description)
    1. [Project Tree](#Project-tree)
    2. [Project structure](#Project-structure)
    3. [Packages for the Ansible](#Packages-for-the-Ansible)
1. [Environment preparations](#Environment-preparations)
2. [AWS account settings](#AWS-account-settings)
3. [Launch ec2 instance](#Launch-ec2-instance)
4. [Molecule tests](#Molecule-tests)
    1. [Create and launch ec2-instance](#Create-and-launch-ec2-instance)
    2. [Install services](#Install-services)
    3. [Verify installation](#Verify-installation)
## Description
___
The main idea was to use __Ansible__ for configuration management.
__Molecule__ for tests. __AWS__ is for Cloud base instances 

### Project tree:
~~~
ansible_test/
├── ansible_key.pem
├── group_vars
│   └── all
├── hosts.txt
├── playbook_aws_service.yml
├── requirements.txt
├── roles
│   ├── apache
│   │   ├── handlers
│   │   │   └── main.yml
│   │   ├── tasks
│   │   │   └── main.yml
│   │   └── templates
│   │       └── index.html
│   ├── aws_create
│   │   └── tasks
│   │       └── main.yml
│   └── fromgit
│       └── tasks
│           └── main.yml
├── service_tests-role
│   ├── defaults
│   │   └── main.yml
│   ├── files
│   ├── handlers
│   │   └── main.yml
│   ├── meta
│   │   └── main.yml
│   ├── molecule
│   │   └── default
│   │       ├── converge.yml
│   │       ├── create.yml
│   │       ├── destroy.yml
│   │       ├── INSTALL.rst
│   │       ├── molecule.yml
│   │       ├── prepare.yml
│   │       ├── tests
│   │       │   └── test_default.py
│   │       └── verify.yml
│   ├── README.md
│   ├── tasks
│   │   └── main.yml
│   ├── templates
│   ├── tests
│   │   ├── inventory
│   │   └── test.yml
│   └── vars
│       └── main.yml
├── var_pass
└── web_page
    └── index.html

~~~
### Project structure:

`playbook_aws_service.yml` - the Ansible playbook that manages main configuration of our ec2 and roles  
`ansible_key.pem` - the key for the account __ec2-user__  
`group_vars` - the directory contains variables credentials to  __ec2 AWS__ instance and connection   
`roles` - the roles tasks directory   
`roles/apache` - the role installs __Apache__ and copy HTML from tha folder __roles/apache/templates__  
`roles/aws_create` - the role contains: 
- create the security group using the ec2_group __Ansible__ module 
- create our server instance using the ec2 __Ansible__ module with this security group
- wait for port 22 to be accessible on the instance and __SSH__ to be available  

`roles/fromgit` - the role install Apache on the host, also firewalld, copy HTML from Git repository and start __Apache__ server  
`service_tests-role` - contain __Molecule__ tests for __Ansible__ roles and playbooks that in isolation launched ec2 instance with the settings of the main project  
`service_tests-role/molecule/default` - the directory contains __Molecule__ configurations  
`service_tests-role/molecule/default/tests` - the directory contains test functions for our services  
`service_tests-role/vars` - the directory containes variables credentials to test instance and connection  
#### P.S.
`/root/.cache/molecule/service_tests-role/default/ssh_key` - __Molecule__ will generate the SSH public key for ec2 test 

### Packages for the Ansible  
 * epel-release
 * ansible2.9
 * python3
 * boto3
 * molecule


## Environment preparations
Be advised we use CentOS7  
1. Install Ansible
```shell
sudo yum install epel-release
sudo yum install ansible
```
OR, Install from RPM if have any problems  
```shell
yum install epel-release-latest-7.noarch.rpm
yum update -y
yum install git python python-devel python-pip openssl ansible -y
```
2. Install boto3 (it needs for __AWS__)
```shell
pip3 install --upgrade pip 
pip install boto boto3
```
3. Install Molecule
```shell
python3 -m pip install --upgrade pip
python3 -m pip install molecule-ec2
```
## AWS account settings
We need to get an AWS account and have Access key (IAM->Access keys) and rechanged data in directory `group_vars` on yours __aws_access_key__ and __aws_secret_key__.  
Also create image in __AWS (AMIs->Launch)__ and reset __image__ in `group_vars`.  
The same changes need to do in `group_vars`.

## Launch ec2 instance
We will first need to create EC2 on the our AWS server.  
I need to mention __aws_access_key__ and __aws_secret_key__ are encrypted by vault and the password located in the file `var_pass`

How we can start playbook?
While in __ansible_test__ folder: 
* First method (the system ask us to confirmation required)
```shell
ansible-playbook --tags "aws, fromgit" -i hosts.txt playbook_aws_service.yml -vvv
```
* Second method (without confirmation required)
```shell
ANSIBLE_HOST_KEY_CHECKING=False ansible-playbook --tags "aws, fromgit" -i hosts.txt playbook_aws_service.yml -vvv
```
* Real method (as so as we use vault for the __aws_access_key__ and __aws_secret_key__)
```shell
ANSIBLE_HOST_KEY_CHECKING=False ansible-playbook --tags "aws, fromgit" -i hosts.txt playbook_aws_service.yml -vvv --ask-vault-pass
```
The password exists in the file `var_pass`  
As an option  
```shell
ANSIBLE_HOST_KEY_CHECKING=False ansible-playbook --tags "aws, fromgit" -i hosts.txt playbook_aws_service.yml -vvv --vault-password-file var_pass
```

## Molecule tests

### Create and launch ec2-instance
We need install an instance, creat a security group and open ports
1. Go to the __service_tests-role__ folder
2. Reset molecule data python3 -m molecule reset
3. Open the file __service_tests-role/molecule/default/molecule.yml__
4. Uncomment the line group_vars: __../../../group_vars__
This is because the molecule creates its own ssh key
And leave comment by group_vars: __../../vars__
5. Enter the command 
```shell
python3 -m molecule create --vault-password-file ../var_pass
```
And wait (You can leave the moment and not wait 3 minutes. __Ctrl+C and then C__)

### Install services                                                               
Role installation (__Apache, firewalld__) and copying a web page

0. Open the file __service_tests-role/molecule/default/molecule.yml__
1. Comment out the line group_vars: __../../vars__  
This is because the molecule creates its own ssh key  
And proceed __../../../group_vars__ leave closed
2. Run the command
```shell
python3 -m molecule converge
```
The task file is located here: __service_tests-role/tasks/main.yml__

### Verify installation
Testing the installation to the instance
```shell
python3 -m molecule verify
```
The tests exist here __service_tests-role/molecule/default/tests__
 - A test checks that ec2-user exists 
 - A test for the presence of a copied file from the git
 - Test for the presence of packages apache, firewalld
 - Test that the Apache service is running
 - A test on availability of listening port IP4
 - A test to having ssh port listening  

 #### P.S.
 The log files are attached to this repository as __Molecule_tests.log__ and __Launch_EC2.log__

License
-------
Beer Here

Author Information
------------------
Maksim Merkulov (https://www.linkedin.com/in/maksim-merkulov/)
