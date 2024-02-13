# Copyright (c) Microsoft. All rights reserved.

from pydantic import BaseModel, ConfigDict


class NodeEngineBaseModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
    )
