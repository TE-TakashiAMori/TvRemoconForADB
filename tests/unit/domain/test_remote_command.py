"""
Remote Command エンティティのテスト
"""
import pytest
from datetime import datetime
from remocon_for_adb.domain.entities.remote_command import RemoteCommand, CommandType, DirectionKey, ButtonKey


class TestRemoteCommand:
    """RemoteCommandエンティティのテストクラス"""

    def test_create_direction_command(self):
        """方向キーコマンド作成のテスト"""
        # Arrange & Act
        command = RemoteCommand.create_direction_command(DirectionKey.UP)
        
        # Assert
        assert command.command_type == CommandType.DIRECTION
        assert command.key_code == DirectionKey.UP.value
        assert command.raw_command == "input keyevent KEYCODE_DPAD_UP"
        assert isinstance(command.timestamp, datetime)

    def test_create_button_command(self):
        """ボタンコマンド作成のテスト"""
        # Arrange & Act
        command = RemoteCommand.create_button_command(ButtonKey.SELECT)
        
        # Assert
        assert command.command_type == CommandType.BUTTON
        assert command.key_code == ButtonKey.SELECT.value
        assert command.raw_command == "input keyevent KEYCODE_DPAD_CENTER"
        assert isinstance(command.timestamp, datetime)

    def test_direction_key_enum_values(self):
        """DirectionKey列挙値のテスト"""
        # Act & Assert
        assert DirectionKey.UP.value == "KEYCODE_DPAD_UP"
        assert DirectionKey.DOWN.value == "KEYCODE_DPAD_DOWN"
        assert DirectionKey.LEFT.value == "KEYCODE_DPAD_LEFT"
        assert DirectionKey.RIGHT.value == "KEYCODE_DPAD_RIGHT"

    def test_button_key_enum_values(self):
        """ButtonKey列挙値のテスト"""
        # Act & Assert
        assert ButtonKey.SELECT.value == "KEYCODE_DPAD_CENTER"
        assert ButtonKey.BACK.value == "KEYCODE_BACK"
        assert ButtonKey.HOME.value == "KEYCODE_HOME"

    def test_command_type_enum_values(self):
        """CommandType列挙値のテスト"""
        # Act & Assert
        assert CommandType.DIRECTION.value == "direction"
        assert CommandType.BUTTON.value == "button"

    def test_create_custom_command(self):
        """カスタムコマンド作成のテスト"""
        # Arrange
        custom_keycode = "KEYCODE_VOLUME_UP"
        
        # Act
        command = RemoteCommand.create_custom_command(custom_keycode)
        
        # Assert
        assert command.command_type == CommandType.CUSTOM
        assert command.key_code == custom_keycode
        assert command.raw_command == f"input keyevent {custom_keycode}"

    def test_command_equality(self):
        """コマンドの同一性テスト"""
        # Arrange
        command1 = RemoteCommand.create_direction_command(DirectionKey.UP)
        command2 = RemoteCommand.create_direction_command(DirectionKey.UP)
        command3 = RemoteCommand.create_direction_command(DirectionKey.DOWN)
        
        # Act & Assert
        assert command1 == command2  # 同じキーコードなら同じ
        assert command1 != command3  # 違うキーコードなら違う

    def test_command_string_representation(self):
        """コマンドの文字列表現テスト"""
        # Arrange
        command = RemoteCommand.create_button_command(ButtonKey.HOME)
        
        # Act
        str_repr = str(command)
        
        # Assert
        assert "KEYCODE_HOME" in str_repr
        assert "button" in str_repr

    def test_is_direction_command(self):
        """方向キーコマンド判定のテスト"""
        # Arrange
        direction_cmd = RemoteCommand.create_direction_command(DirectionKey.LEFT)
        button_cmd = RemoteCommand.create_button_command(ButtonKey.BACK)
        
        # Act & Assert
        assert direction_cmd.is_direction_command() is True
        assert button_cmd.is_direction_command() is False

    def test_is_button_command(self):
        """ボタンコマンド判定のテスト"""
        # Arrange
        direction_cmd = RemoteCommand.create_direction_command(DirectionKey.RIGHT)
        button_cmd = RemoteCommand.create_button_command(ButtonKey.SELECT)
        
        # Act & Assert
        assert direction_cmd.is_button_command() is False
        assert button_cmd.is_button_command() is True

    def test_from_string_direction(self):
        """文字列からの方向キーコマンド作成テスト"""
        # Arrange & Act
        command = RemoteCommand.from_string("up")
        
        # Assert
        assert command.command_type == CommandType.DIRECTION
        assert command.key_code == DirectionKey.UP.value

    def test_from_string_button(self):
        """文字列からのボタンコマンド作成テスト"""
        # Arrange & Act
        command = RemoteCommand.from_string("home")
        
        # Assert
        assert command.command_type == CommandType.BUTTON
        assert command.key_code == ButtonKey.HOME.value

    def test_from_string_invalid(self):
        """無効な文字列からのコマンド作成エラーテスト"""
        # Arrange & Act & Assert
        with pytest.raises(ValueError):
            RemoteCommand.from_string("invalid_key")

    def test_validate_timing(self):
        """コマンド実行タイミングのテスト"""
        # Arrange
        command1 = RemoteCommand.create_direction_command(DirectionKey.UP)
        command2 = RemoteCommand.create_direction_command(DirectionKey.DOWN)
        
        # Act & Assert
        assert command2.timestamp >= command1.timestamp
