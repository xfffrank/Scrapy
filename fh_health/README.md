## fh_health
> http://zzk.fh21.com.cn/letter/symptoms/A.html

### 爬虫目标
提取全部症状的简介，相似症状，以及可能引起该症状的疾病。

### 笔记
* 三部分信息位于不同但相似的 url 地址，我对每个症状使用了三个 Request 对象来处理，这样有一个问题，就是信息是分散的，无法 yield 一个统一的 item 交给 pipeline 处理，也给去重带来了麻烦。于是我直接在 pipeline 中写了操作数据库的类方法，在 spider 中直接调用，跳过了 yield item 的环节。
* 一开始使用了 Python 的内置函数 map 来节省代码量，后来程序跑起来发现爬取速度堪忧，review 了代码后怀疑是 map 函数的问题。Google 一下发现 map 的性能确实不是很高，而且我还在 map 里面用了匿名函数。改成列表生成式以后爬虫的速度果然蹭蹭上去了。