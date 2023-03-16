
# aws-data-analytics-course

> &nbsp;
> :warning: **This is a work in progress**: 
> - Running the deployment commands will create aws infrastructure under your own account and incur charges. 
> - Some elements are created with admin roles to simplfy stack creation for demonstration.
> &nbsp;

This repo details exercises and learnings form the udemy data analytics course.

Each section contains a cdktf terraform stack to replicate exercises from within the course.

## Prerequisites

- AWS Credentials to programmaticly connect to your aws account

- Install Terraform CDKTF 
```bash
npm install --global cdktf-cli@latest
```
- Create a .env file within the root of this repo with the following values
```txt
ENV=< string identifier for an environment e.g. dev >
REGION=< your aws region >
ACCOUNT_ID=< your aws account id >
KEY_PAIR_NAME=< your aws key pair name >
```
[https://developer.hashicorp.com/terraform/tutorials/cdktf/cdktf-install](https://developer.hashicorp.com/terraform/tutorials/cdktf/cdktf-install)
## Usage


To deploy 

```
cdktf deploy
```


NOTE: To deploy a single section. Edit main.py and comment out the relevant sections from `MyCourseStack`.

To destroy
```
cdktf destroy
```


## Section Two

## Section Three

## Troubleshooting


##### Error: Module not installed
This error currently has an open github issue and can be resolved by removing the cdktf.out folder and re-run the deployment steps.


