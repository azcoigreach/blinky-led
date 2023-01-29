import os

from pydantic import BaseSettings

def get_home_dir():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    
class Matrix(BaseSettings):
    rows: int = 32
    cols: int = 32
    chain_length: int = 1
    parallel: int = 1
    hardware_mapping: str = "regular"
    pwm_bits: int = 11
    pwm_lsb_nanoseconds: int = 130
    pwm_dither_bits: int = 0
    brightness: int = 100
    gpio_slowdown: int = 1
    scan_mode: int = 0
    show_refresh_rate: int = 0
    inverse_colors: int = 0
    multiplexing: int = 0
    row_address_type: int = 0
    disable_hardware_pulsing: int = 0
    led_rgb_sequence: str = "RGB"
    pixel_mapper_config: str = ""
    panel_type: str = ""
    limit_refresh_rate_hz: int = 0
    daemon: int = 0
    drop_privileges: int = 0

    class Config:
        env_file = os.path.join(get_home_dir(), ".env")
        env_file_encoding = "utf-8"
        env_prefix = "MATRIX_"

matrix = Matrix()