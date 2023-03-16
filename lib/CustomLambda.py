#!/usr/bin/env python
from constructs import Construct

from cdktf import TerraformOutput, RemoteBackend, TerraformAsset, AssetType, Resource

from imports.aws.s3_bucket import S3Bucket
from imports.aws.s3_object import S3Object
from imports.aws.iam_role import IamRole
from imports.aws.iam_policy_attachment import IamPolicyAttachment
from imports.aws.iam_role_policy_attachment import IamRolePolicyAttachment
from imports.aws.lambda_function import LambdaFunction
from imports.aws.lambda_function_event_invoke_config import (
    LambdaFunctionEventInvokeConfig,
)
from imports.aws.lambda_event_source_mapping import LambdaEventSourceMapping


from lib.EnvironmentOptions import EnvironmentOptions

import os
import os.path as Path
import json

from shortuuid import uuid


class LambdaOptions:
    def __init__(
        self,
        name: str,
        asset_path: str,  # relative to root of repo cwd
        version: str,
        handler: str,
        runtime: str,
        stage: str,
        lambda_role_polices: list[str] = None,
        event_mapping_arn: str = None,
    ) -> None:
        self.name = name
        self.asset_path = asset_path
        self.version = version
        self.handler = handler
        self.runtime = runtime
        self.stage = stage
        self.lambda_role_polices = lambda_role_polices
        self.event_mapping_arn = event_mapping_arn


# https://github.com/cdktf/cdktf-integration-serverless-python-example/blob/main/posts/api/index.py


class CustomLambda(Resource):
    default_lambda_role_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Action": "sts:AssumeRole",
                "Principal": {"Service": "lambda.amazonaws.com"},
                "Effect": "Allow",
                "Sid": "",
            }
        ],
    }

    def __init__(
        self,
        scope: Construct,
        id: str,
        options: EnvironmentOptions,
        lambda_options: LambdaOptions,
    ):
        self.lambda_options = lambda_options
        super().__init__(scope, id)

        #  create lambda asset
        asset = TerraformAsset(
            self,
            "lambda-asset-" + uuid(),
            path=Path.join(os.getcwd(), self.lambda_options.asset_path),
            type=AssetType.ARCHIVE,
        )

        # create bucket
        bucket = S3Bucket(
            self,
            "bucket" + uuid(),
            bucket_prefix=f"lambda-{self.lambda_options.name.lower()}",
        )

        # upload asset to bucket
        lambda_archive = S3Object(
            self,
            "lambda-archive-" + uuid(),
            bucket=bucket.bucket,
            key=f"{self.lambda_options.name}/{self.lambda_options.version}/{asset.file_name}",
            source=asset.path,
        )

        # create role
        lambda_role = IamRole(
            self,
            "lambda-role-" + uuid(),
            name=f"{self.lambda_options.name.lower()}-lambda-role",
            assume_role_policy=json.dumps(self.default_lambda_role_policy, indent=4),
        )

        if self.lambda_options.lambda_role_polices:
            for p in self.lambda_options.lambda_role_polices:
                IamRolePolicyAttachment(
                    self,
                    "lambda-role-policy-" + uuid(),
                    policy_arn=p,
                    role=lambda_role.name,
                )
        else:
            # add policy to role
            IamRolePolicyAttachment(
                self,
                "lambda-role-policy-" + uuid(),
                policy_arn="arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole",
                role=lambda_role.name,
            )

        # create the lambda function
        self.lambda_function = LambdaFunction(
            self,
            "lambda-" + uuid(),
            function_name=f"{self.lambda_options.name}",
            s3_bucket=bucket.bucket,
            s3_key=lambda_archive.key,
            handler=self.lambda_options.handler,
            runtime=self.lambda_options.runtime,
            role=lambda_role.arn,
        )

        if self.lambda_options.event_mapping_arn:
            LambdaEventSourceMapping(
                self,
                "event-mapping-" + uuid(),
                event_source_arn=self.lambda_options.event_mapping_arn,
                function_name=self.lambda_function.arn,
                starting_position="LATEST",
            )
