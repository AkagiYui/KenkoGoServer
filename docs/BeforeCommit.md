# 提交前检查！

## 编写 更新日志

## 版本号 信息修改

(src/module/global_dict)

VERSION_NUM 加一

VERSION_STR 修改

## 导入排序

```shell
isort src/
```

## 代码规范

```shell
flake8 src/ --max-line-length=127 --ignore=W503 --statistics --count
mypy src/ --show-error-codes --follow-imports=skip --ignore-missing-imports --exclude src/module/atomicwrites
```

## 更新 依赖表

检查 `requirements*.in` 文件

```shell
# 生成 requirements*.txt
pip-compile  --annotation-style=line
```


