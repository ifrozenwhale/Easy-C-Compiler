# 词法分析器

## 运行

使用`main.py`修改测试文件路径即可

## 概况

使用python实现一个简单的C子集的编译器

该程序使用python语言实现了C语言子集的词法分析程序。具体实现了

- 识别给定的C语言子集的单词符号，并以(token, attribute)的形式输出。
- 包含int（10进制，8进制，16进制）,_+,-,*,/,=,==,>,<,<>,>=,<=,!,&&,||,**&,|**,if,**else,**while,get,put等**必做**和**可选项**。
- 可以识别并跳过源程序的**（多个）**空白
- 支持**预处理**，预处理将**跳过代码中的注释**（包括单行注释//和多行注释//），删除部分字符（代码长度压缩**），包括删除多余的空格（连续空格只保留一个），删除换行符、制表符等。
- 支持检查代码中的**所有**词法错误，出现错误时将报告错误所在的**代码行**（如果进行了预处理，则代码行号失去意义）以及在所有字符中的位置索引。出现错误时，将**跳过**错误所在的单词。
- 可以统计代码的行数，字符数以及单词频数。

## 错误处理说明

针对状态机的每一个状态设置错误处理。具体的，对于边界符号而言，这里认为不存在错误（单符号）；对于其他的，若当前状态接收的字符不在允许的范围内（状态图上所示，以及边界符），则表示出错。例如变量名以数字开头或者非字母字符开头（9az）则认为错误；对于10进制整数，判断范围为0-9999，超过9999或者有小数点等均为错误；对于8进制数和16进制数也进行处理。特别的，十六进制以0x开头且可以允许前导0，如0x00000f。在存储时，将读取的8进制和16进制整数10进制形式存储。

当遇到错误时，打印错误类型和所在代码行数以及字符位置，并跳过当前错误所在单词（以分界符为间隔）。

## 实现

程序使用Python实现，便于利用字典等数据结构，考虑到实验性质，**没有**利用python处理字符串的一些函数，如`replace`等批量替换删除，而是使用字符逐个扫描的方式。程序以面向对象的方式实现。

- `init`，定义`other_char_list`包含换行符、制表符等，定义`border_char_list`表示边界符号，定义`reserved_words_list`表示保留字，定义`token_list`表示记号列表，`symbol_table`符号表，`attr_dict`表示符号属性翻译表。

- 定义`print_line`函数，打印分割线，如：

![img](https://frozenwhale.oss-cn-beijing.aliyuncs.com/img/clip_image002.png)

- 定义`filter`函数，进行文本预处理。将跳过代码注释（单行//和多行/**/），如果遇到注释不匹配，例如最后只有一个/，将抛出异常，告知错误终止程序。还可以选择将代码中的连续空格进行压缩，将换行符等删除。

- 定义`insert_symbol`函数，进行符号表的插入，并维护符号表指针（通过建立符号表id字典实现）。

- 定义`insert_token`函数，进行记号token的插入，使用元组(token, attribute)的结构。

- 定义`print_error`函数，打印错误信息和错误发生的位置。格式为：

  ```python
  error {info} at line {error_line}, char at {error_pos }
  ```

  

- 定义`scanner`函数，进行文本的扫描。整个扫描逻辑基于状态机图实现。

  通过在开始识别新的单词符号之前，识别（多个）空格、换行符等并跳过，并记录行数。

  由于python语言中没有switch-case语句，因此通过字典映射函数的方式实现状态机。定义子函数caseid，结构大体如下：

  ```python
  def caseid(token,c):
  
  if c == symbol_x:
  
    return state_id
  
  elif c in border_char_list:
  
    insert(token, token.attribute)
  
    return 0
  
  else:
  
    print_error(error_info)
  
    return -1
  
  
  ```

  

  函数接收一个token记号串，以及下一个输入字符c，如果匹配，则进行状态转移到state_x；否则如果c是边界字符，则将token写入记号表；否则遇到错误打印错误信息，返回-1.

  通过定义字典

  ```python
  switch={0:case0,1:case1,…,id:caseId}
  ```

  以字典函数调用的方式实现switch-case，返回值state分为0，>0以及-1.

  ```python
  state = switch [state](token, c)
  ```

  
  - 0表示起点，需要清空token字符串并处理空格等信息
  - \>0表示对应的状态
  - -1表示错误，需要跳过单词（包括空格）等。

- 定义`run`函数，依次进行文件加载，预处理`filter`，字符扫描`scanner`，并输出`token_list`. 

- 定义`print_static_data`函数，打印统计信息（不包括注释）

## 结果

![image-20210418234250718](https://frozenwhale.oss-cn-beijing.aliyuncs.com/img/image-20210418234250718.png)

![image-20210418234306711](https://frozenwhale.oss-cn-beijing.aliyuncs.com/img/image-20210418234306711.png)

![image-20210418234326797](https://frozenwhale.oss-cn-beijing.aliyuncs.com/img/image-20210418234326797.png)

