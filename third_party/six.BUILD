# Copied from https://github.com/protocolbuffers/protobuf/blob/master/six.BUILD

load("@rules_python//python:defs.bzl", "py_library")

genrule(
  name = "copy_six",
  srcs = ["six-1.10.0/six.py"],
  outs = ["six.py"],
  cmd = "cp $< $(@)",
)

py_library(
  name = "six",
  srcs = ["six.py"],
  srcs_version = "PY2AND3",
  visibility = ["//visibility:public"],
)
