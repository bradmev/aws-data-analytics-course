#!/usr/bin/env python
from constructs import Construct

from cdktf import TerraformOutput, RemoteBackend, TerraformAsset, AssetType, Resource

from imports.aws.s3_bucket import S3Bucket
from imports.aws.s3_object import S3Object

from lib.EnvironmentOptions import EnvironmentOptions


class BucketOptions:
    def __init__(
        self,
        name: str,
        force_destroy: str,
    ) -> None:
        self.name = name
        self.force_destroy = force_destroy


class CustomBucket(Resource):
    def __init__(
        self,
        scope: Construct,
        id: str,
        options: EnvironmentOptions,
        bucket_options: BucketOptions,
    ):
        self.bucket_options = bucket_options
        super().__init__(scope, id)

        self.bucket = S3Bucket(
            self,
            id,
            bucket=self.bucket_options.name,
            force_destroy=self.bucket_options.force_destroy,
        )
