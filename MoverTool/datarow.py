"""
Class to map data rows from the games workbook for easier parsing
"""

from typing import Optional

import numpy as np
from pydantic import BaseModel, ConfigDict, Field, field_validator


class DataRow(BaseModel):
    """
    Class to map data rows from the games workbook for easier parsing
    """
    model_config = ConfigDict(extra="ignore")
    game_name: str = Field(alias="Game")
    size: float = Field(alias="Size in GB")
    include: Optional[bool] = Field(alias="Include?")

    @field_validator("include", mode="before")
    @classmethod
    def validate_include(cls, value):
        """
        Validate the "Include?" field to ensure it is a boolean value, can be a numpy NaN,
        or a string representation of a boolean

        :param Any value: The value to validate
        :raises ValueError: If the value is not a valid boolean or NaN
        :return: The validated boolean value or None if it is NaN
        :rtype: Optional[bool]
        """
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            value = value.strip().lower()
            if value in {"yes", "y", "true", "t", "1"}:
                return True
            elif value in {"no", "n", "false", "f", "0"}:
                return False
        if isinstance(value, (float, np.floating)) and np.isnan(value):
            return None
        raise ValueError(f"Invalid value for 'Include?': {value}")
