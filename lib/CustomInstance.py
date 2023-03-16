#!/usr/bin/env python
from constructs import Construct

from cdktf import TerraformOutput, RemoteBackend, TerraformAsset, AssetType, Resource

from imports.aws.s3_bucket import S3Bucket
from imports.aws.s3_object import S3Object
from imports.aws.instance import Instance

from imports.aws.iam_policy import IamPolicy
from imports.aws.iam_role import IamRole
from imports.aws.iam_policy_attachment import IamPolicyAttachment
from imports.aws.iam_role_policy_attachment import IamRolePolicyAttachment
from imports.aws.iam_instance_profile import IamInstanceProfile

from lib.EnvironmentOptions import EnvironmentOptions
import json


class InstnaceOptions:
    def __init__(
        self,
        name: str,
        ami: str,
        instance_type: str,
        key_name: str,
        user_data: str,
        iam_instance_profile_name: str,
        subnet_id: str,
        associate_public_ip_address: bool,
        security_groups: list[str],
    ) -> None:
        self.name = name
        self.ami = ami
        self.instance_type = instance_type
        self.key_name = key_name
        self.user_data = user_data
        self.iam_instance_profile_name = iam_instance_profile_name
        self.subnet_id = subnet_id
        self.associate_public_ip_address = associate_public_ip_address
        self.security_groups = security_groups


class CustomInstance(Resource):
    instance: Instance

    def __init__(
        self,
        scope: Construct,
        id: str,
        options: EnvironmentOptions,
        instance_options: InstnaceOptions,
    ):
        self.instance_options = instance_options
        self.env_options = options
        super().__init__(scope, id)

        # # create policy content
        # assume_role_policy = {
        #     "Version": "2012-10-17",
        #     "Statement": [
        #         {
        #             "Action": "sts:AssumeRole",
        #             "Principal": {"Service": "ec2.amazonaws.com"},
        #             "Effect": "Allow",
        #             "Sid": "",
        #         }
        #     ],
        # }

        # # create role
        # instance_profile_role = IamRole(
        #     self,
        #     "role",
        #     name=f"-role",
        #     assume_role_policy=json.dumps(self.assume_role_policy, indent=4),
        #     managed_policy_arns=["arn:aws:iam::aws:policy/AdministratorAccess"],
        # )

        # instance_profile = IamInstanceProfile(name="", role=instance_profile_role.name)

        instance = Instance(
            self,
            "instance",
            tags={"Name": self.instance_options.name},
            # name=self.instance_options.name,
            ami=self.instance_options.ami,
            instance_type=self.instance_options.instance_type,
            key_name=self.instance_options.key_name,
            user_data=self.instance_options.user_data,
            iam_instance_profile=self.instance_options.iam_instance_profile_name,
            subnet_id=self.instance_options.subnet_id,
            associate_public_ip_address=self.instance_options.associate_public_ip_address,
            # security_groups=self.instance_options.security_groups,
            vpc_security_group_ids=self.instance_options.security_groups,
        )
