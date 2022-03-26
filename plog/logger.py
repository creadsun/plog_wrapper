# coding=utf-8
# Auth: Creads <865363864@qq.com>
# log the invoke-status for a function
#

import re
import json
import logging
import sys
from functools import wraps
from logging import Formatter
from logging import StreamHandler

LOGGER_NAME = "plog"

LINE_FORMAT = "%(asctime)s %(levelname)-8s %(threadName)-30s " \
                   "[%(filename)s:%(module)s#%(lineno)d]: %(message)s"
DATE_FORMAT = "%Y/%m/%d %H:%M:%S"

creads_logger = logging.getLogger(LOGGER_NAME)


def get_logger():
    """get the global logger for plog"""
    return creads_logger


def set_logger():
    """set the global logger for plog"""
    global creads_logger
    creads_logger = logger


def configure_logger(level):
    """configure logging"""
    logger = get_logger()

    # Don't add handler twice
    if not logger.handlers:
        stream_handler = StreamHandler(sys.stdout)
        formatter = Formatter(
            fmt=LINE_FORMAT,
            datefmt=DATE_FORMAT,
        )
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)

    logger.setLevel(level)

    return logger


def log_invoke(logger=None,
               level=logging.DEBUG,
               module=None,
               summary=True,
               independent=False,
               result_adapter=None):
    #
    # log the invoke-status for a function
    # :param logger:
    #     - 使用的 logger-handler
    # :param summary:
    #     - true 同时记录调用参数和返回结果，
    #     - false 只记录调用参数
    # :param level
    #     - 日志级别，如果小于配置的展示级别，则无计算无记录
    # :param module
    #     - 被调用方法所属模块（建议: __name__ ）
    # :param independent:
    #     - 是否是独立方法/静态函数，默认 false
    # :param result_adapter:
    #     - default:None
    #     - 返回结果适配器（提炼返回结果的精简/有效内容）
    # :return: A function that wraps the function being decorated.
    # e.g.
    # - @log_invoke(summary=True, independent=True)
    # - def add(a,b):
    # -     return a+b
    # -
    # - add(2,b=8)
    # -------------------
    # - log:
    # - 2022/03/22 11:08:23 DEBUG MainThread [test.py:test#8]: call add(2, b=8) ---> (10)
    #
    logger = logger or get_logger()

    def to_str(arg):
        """将任意类型的变量转化为 str 格式"""
        if arg is None:
            return "None"
        try:
            return json.dumps(arg)
        except TypeError:
            pass

        if isinstance(arg, list):
            list_inner_strs = [to_str(node) for node in arg]
            return '[' + ', '.join(list_inner_strs) + ']'
        if isinstance(arg, tuple):
            tuple_inner_strs = [to_str(node) for node in arg]
            return '(' + ', '.join(tuple_inner_strs) + ')'
        if isinstance(arg, dict):
            dict_inner_strs = [
                '%s: %s' % (to_str(k), to_str(v)) for (k, v) in arg.items()
            ]
            return '{' + ', '.join(dict_inner_strs) + '}'
        if hasattr(arg, "__class__"):
            try:
                arg_json = json.dumps(
                    arg,
                    sort_keys=True,
                    indent=4,
                    default=lambda o: o.__dict__ if hasattr(o, "__dict__") else repr(o)
                )
                return '%s|%s' % (arg.__class__.__name__, arg_json)

            except TypeError:
                pass
            return '%s|Instance' % arg.__class__.__name__
        if hasattr(arg, "__name__"):
            return '%s|Type' % arg.__class__.__name__
        return repr(arg)

    def arg_formatter(*args, **kwargs):
        """
        将参数格式化
         - 对于 sum = get_sum(1, 2, 3, d=4, e=5)
         - 返回"1, 2, 3, d=4, e=5"
        @param args:
        @param kwargs:
        @return:
        """
        unnamed_part = [
            to_str(args[i]) for i in range(0 if independent else 1, len(args))
        ]
        named_part = ["%s=%s" % (k, to_str(v)) for (k, v) in kwargs.items()]
        return ", ".join(unnamed_part + named_part)

    def result_formatter(result):
        """
        将返回结果格式化，允许自定义精简方法
        @param result:
        @return:
        """
        if result_adapter is not None:
            result = result_adapter(result)
        return to_str(result)

    def get_callee(func, args):
        """
        获取调用名，格式:
        - [module]::[class name (非独立方法才有) ]::[method name]
        @param func:
        @param args:
        @return:
        """
        callee = func.__name__
        if module is not None:
            if (not independent) and len(args) > 0:
                if hasattr(args[0], "__name__"):
                    callee = "%s::%s" % (args[0].__name__, callee)
                elif hasattr(args[0], "__class__"):
                    callee = "%s::%s" % (args[0].__class__.__name__, callee)
            callee = "%s::%s" % (module, callee)
        return callee

    def log(msg):
        """记录日志，去掉换行，适配调用栈层数"""
        msg = re.sub(r'(\r\n)|(\r)|(\n)|(\t)[hg]', '', msg)
        while True:
            tmp = msg.replace("  ", " ")
            if msg == tmp:
                break
            msg = tmp
        logger.log(level, msg, stacklevel=3)

    def decorator(func):
        """装饰器，记录调用日志，执行实际调用"""

        @wraps(func)
        def invoker(*args, **kwargs):
            # 如果展示日志级别 小于 要输出的日志级别，则跳过日志逻辑。
            need_log = level >= logger.level
            callee_str = ""
            args_str = ""
            if need_log:
                callee_str = get_callee(func=func, args=args)
                args_str = arg_formatter(*args, **kwargs) or ""
                if not summary:
                    # 只记录调用参数的日志
                    log("call %s(%s)" % (callee_str, args_str))

            result = func(*args, **kwargs)
            if need_log and summary:
                result_str = result_formatter(result)
                # 同时记录调用参数和返回结果的日志
                log("call %s(%s) ---> (%s)" % (callee_str, args_str, result_str))
            return result

        return invoker

    return decorator
