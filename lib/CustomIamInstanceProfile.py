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


class IamInstnaceProfileOptions:
    def __init__(
        self,
        name: str,
        arns: str,
    ) -> None:
        self.name = name
        self.arns = arns


class CustomIamInstanceProfile(Resource):
    def __init__(
        self,
        scope: Construct,
        id: str,
        options: EnvironmentOptions,
        iam_instance_profile_options: IamInstnaceProfileOptions,
    ):
        self.iam_instance_profile_options = iam_instance_profile_options
        self.env_options = options
        super().__init__(scope, id)

        # create policy content
        assume_role_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Action": "sts:AssumeRole",
                    "Principal": {"Service": "ec2.amazonaws.com"},
                    "Effect": "Allow",
                    "Sid": "",
                }
            ],
        }

        # create role
        instance_profile_role = IamRole(
            self,
            "role",
            name=f"{self.iam_instance_profile_options.name}-role",
            assume_role_policy=json.dumps(assume_role_policy, indent=4),
            managed_policy_arns=self.iam_instance_profile_options.arns,
        )

        self.iam_instance_profile = IamInstanceProfile(
            self,
            "instance-profile",
            name=self.iam_instance_profile_options.name,
            role=instance_profile_role.name,
        )
