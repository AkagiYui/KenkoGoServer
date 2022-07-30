import argparse
import contextlib
import signal
import sys

from rich.traceback import install as install_rich_traceback

from module.command_handler import CommandHandler
from module.console import Console
from module.global_dict import Global
from module.logger_ex import LoggerEx, LogLevel
from module.user_config import UserConfig


class Main:
    """也许是不必要的面向对象？"""

    def signal_handler(self, sign, _) -> None:
        """信号处理器"""
        if sign in (signal.SIGINT, signal.SIGTERM):
            self.log.debug(f'Received signal {sign}, Application exits.')
            Global().time_to_exit = True

    def __init__(self):
        Global().console = Console()  # 初始化控制台对象
        install_rich_traceback(console=Global().console, show_locals=True)  # 捕获未处理的异常

        # 命令行参数解析
        parser = argparse.ArgumentParser(
            description=f'{Global().app_name} - {Global().description}',  # 应用程序的描述
            add_help=False,  # 不输出自动生成的说明
            exit_on_error=False,  # 发生错误时不退出
        )
        parser.add_argument('-h', '--help', action='store_true', help='Show this help message and exit')
        parser.add_argument('-a', '--auto-start', action='store_true', help='Auto start go-cqhttp')
        parser.add_argument('-d', '--debug', action='store_true', help='Debug mode')
        parser.add_argument('-c', '--config', help='Config file path', default='config.yaml')
        args_known, args_unknown = parser.parse_known_args()

        # 如果用户输入了 -h 或 --help，则显示帮助信息并退出
        if args_known.help:
            parser.print_help()
            sys.exit(0)

        Global().auto_start = args_known.auto_start
        Global().debug_mode = args_known.debug or Global().debug_mode  # 开启调试模式

        # 创建日志打印器
        self.log: LoggerEx = LoggerEx(self.__class__.__name__)
        self.log.set_level(LogLevel.DEBUG if Global().debug_mode else LogLevel.INFO)

        Global().user_config = UserConfig(args_known.config)  # 加载用户配置

        # 设置信号响应
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

        Global().command_handler = CommandHandler()  # 创建命令处理器
        self.run_forever()  # 启动程序

    def run_forever(self) -> None:
        """运行并阻塞"""
        self.log.debug(f'{Global().app_name} Starting...')
        app = None

        try:
            # 启动应用
            from kenko_go import KenkoGo
            app = KenkoGo()
            app.start()
        except Exception as e:
            self.log.exception(e)
            Global().time_to_exit = True
            self.log.critical('Critical Error, Application exits abnormally.')  # 发生致命错误，应用异常退出

        while not Global().time_to_exit:
            try:
                command = Global().console.input('> ')  # 获取用户输入
            except (UnicodeDecodeError, EOFError, KeyboardInterrupt):
                if Global().time_to_exit:
                    break  # 退出
                else:
                    self.log.error('Invalid Command')  # 输入的命令无效
            else:
                Global().command_handler.add(command)

        # 退出程序
        from kenko_go import KenkoGo
        if isinstance(app, KenkoGo):
            app.stop()
        self.log.debug(f'{Global().app_name} Exits.')
        sys.exit(Global().exit_code)


if __name__ == '__main__':
    # Windows下修改控制台窗口标题
    with contextlib.suppress(Exception):
        import ctypes
        ctypes.windll.kernel32.SetConsoleTitleW(f'{Global().app_name} {Global().version_str}')

    # 让PyCharm调试输出的信息换行
    if sys.gettrace() is not None:
        print('Debug Mode')
        Global().debug_mode = True

    sys.exit(Main())  # 启动程序
