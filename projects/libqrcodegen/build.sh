#!/bin/bash -eu
# Copyright 2020 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
################################################################################

# build project
# e.g.
pushd c
make -j libqrcodegen.a
popd
pushd cpp
make -j libqrcodegen.a
popd

$CXX $CXXFLAGS -std=c++11 -Ic/ \
    $SRC/encode_binary_c_fuzzer.cpp -o $OUT/encode_binary_c_fuzzer \
    $LIB_FUZZING_ENGINE -Lc -lqrcodegen

$CXX $CXXFLAGS -std=c++11 -Icpp/ \
    $SRC/encode_binary_cpp_fuzzer.cpp -o $OUT/encode_binary_cpp_fuzzer \
    $LIB_FUZZING_ENGINE -Lcpp -lqrcodegen
