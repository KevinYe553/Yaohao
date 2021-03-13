import re
from collections import Counter
import matplotlib.pyplot as plt

# 实例化一个counter对象
count = Counter()

# 将所有的姓氏正则匹配出来
with open('./yaohao_data_analysis.txt','r',encoding="utf-8")as f:
	text = f.read()
f_name_list = re.findall(r'[\u4E00-\u9FA5]',text)
				
for n in f_name_list:
	count[n] += 1	
	
# 将count转成字典	
d = dict(count)

# 将无序的字典进行排序
def dict_sort(dic):
	l=list(dic.items())      
	l.sort(key=lambda x:x[1],reverse=True) 
	return l
 
key=[]
value=[]
for k,v in dict_sort(d):
	key.append(k)
	value.append(v)

# 生成条形图	
# 这两行代码解决 plt 中文显示的问题
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

plt.bar(key[:20], value[:20])
plt.title('摇号分析条形图')
plt.show()
