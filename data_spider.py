import re
import requests
# import redis
from lxml import etree
from multiprocessing.dummy import Pool
from retrying import retry



class HZ_license_lottery:
	def __init__(self,phase_no):
		self.phase_no = phase_no
		# self.conn = redis.Redis(host='127.0.0.1', port=6379)
		self.run_spider()
		
	@retry(wait_fixed = 3, stop_max_attempt_number = 5)
	def request(self,page_no,phase_no):
		headers = {
			'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36 Edg/88.0.705.74',
		}

		data = {
		  'pageNo': page_no,
		  'issueNumber': phase_no,
		  'applyCode': ''
		}

		response = requests.post('https://apply.hzxkctk.cn/apply/app/status/norm/personPTC', headers=headers, data=data, timeout=5)
		return response.text

	def parse(self,response_data):
		tree = etree.HTML(response_data)
		apply_code = tree.xpath('//*[@id="queryManage"]/table[2]//tr[@class="content_data"]/td[1]/text()|//*[@id="queryManage"]/table[2]//tr[@class="content_data1"]/td[1]/text()')
		applyer_first_name = tree.xpath('//*[@id="queryManage"]/table[2]//tr[@class="content_data"]/td[2]/text()|//*[@id="queryManage"]/table[2]//tr[@class="content_data1"]/td[2]/text()')
		data = dict(zip(apply_code,applyer_first_name))
		return data

	def get_total_pages_num(self,phase_no):
		response_data = self.request(1,phase_no)
		return re.findall("pageCount = window\.parseInt\('(\d+)',\d+\),",response_data)[0]
		
	def load_to_db(self,datas):
		for data in datas:
			for k,v in data.items():
				self.conn.hset(self.phase_no,k,v)
	
	def load_to_txt_file(self,datas):
		first_name_list = []
		for data in datas:
			for k,v in data.items():
				first_name = re.findall('(.*?)\*\*',v)[0]
				first_name_list.append(first_name)
		with open('yaohao_data_analysis.txt','a',encoding='utf-8')as f:
			f.write(' '.join(first_name_list))		
	
	def run_spider(self):
		print(f'开始爬取第{self.phase_no}期数据！')
		data_list = []
		for i in range(1,int(self.get_total_pages_num(self.phase_no))+1):
			print(f'当前请求第{self.phase_no}期的{i}页。')
			try:
				data_list.append(self.parse(self.request(i,self.phase_no)))
			except Exception:
				error = f'第{self.phase_no}期的{i}页,爬取失败！\n'
				with open('log.txt','a',encoding='utf-8')as f:
					f.write(error)
				print(error)
		# self.load_to_db(data_list)
		self.load_to_txt_file(data_list)
		print(f'{self.phase_no}期爬取完成！')
				


def get_phase_no():
	headers = {
		'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36 Edg/88.0.705.74',
	}
	data = {
	  'pageNo': 1,
	  'issueNumber': 202101,
	  'applyCode': ''
	}
	response = requests.post('https://apply.hzxkctk.cn/apply/app/status/norm/personPTC', headers=headers, data=data).text
	tree = etree.HTML(response)
	phase_list = tree.xpath('//*[@id="issueNumber"]/option/text()')[1:]
	return phase_list
	

pool = Pool()
pool.map(HZ_license_lottery,get_phase_no())
pool.close()
pool.join()


