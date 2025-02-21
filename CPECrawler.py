import requests
from bs4 import BeautifulSoup
import os
import re
from urllib.parse import urljoin
import warnings

warnings.filterwarnings("ignore", category=requests.packages.urllib3.exceptions.InsecureRequestWarning)

def sanitize_filename(filename):
    return re.sub(r'[\\/*?:"<>|\n\t]', "", filename).strip()

def download_and_save(link, filename_prefix, folder='CPE/test'):
    try:
        os.makedirs(folder, exist_ok=True)
        response = requests.get(link, verify=False)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        for i, pre_tag in enumerate(soup.find_all('pre')):
            with open(f'{folder}/{filename_prefix}_{i+1}.txt', 'w', encoding='utf-8') as f:
                f.write(pre_tag.text.strip())
    except Exception as e:
        print(f"下載失敗: {link}，錯誤: {e}")

def main():
    url = 'https://cpe.cse.nsysu.edu.tw/cpe/test_data/2020-05-26'

    # 從URL提取日期並創建對應資料夾
    date = url.split('/')[-1]
    base_folder = f'CPE/{date}'
    code_folder = f'{base_folder}/code'
    test_folder = f'{base_folder}/test'
    
    # 創建所需的資料夾
    os.makedirs(code_folder, exist_ok=True)
    os.makedirs(test_folder, exist_ok=True)
    
    response = requests.get(url, verify=False)
    
    if response.status_code != 200:
        print(f"無法訪問該網站，狀態碼: {response.status_code}")
        return
        
    soup = BeautifulSoup(response.content, 'html.parser')

    # 提取PDF連結
    pdf_links = [urljoin(url, link['href']) for link in soup.find_all('a', href=True) 
                if 'problemPdf' in link['href'] and link['href'].endswith('.pdf')]
    print("找到的 PDF 連結:", *pdf_links, sep='\n')

    # 提取與下載程式碼
    code_links = [link['href'] for link in soup.find_all('a', href=True)
                 if 'problemPdf' in link['href'] and link['href'].endswith('.php') 
                 and 'testData' not in link['href']]

    for code_link in code_links:
        code_response = requests.get(code_link, verify=False)
        if code_response.status_code == 200:
            code_soup = BeautifulSoup(code_response.content, "html.parser")
            if code_section := code_soup.find("pre", class_="prettyprint"):
                code_text = code_section.get_text().strip()
                if "//uva" in code_text:
                    filename = re.search(r'//uva(\d+)', code_text)
                    filename = filename.group(1) if filename else "unknown"
                    # 修改儲存路徑到code資料夾
                    with open(f"{code_folder}/uva_{filename}.cpp", "w", encoding="utf-8") as file:
                        file.write(code_text)
                    print(f"程式碼已儲存為 {code_folder}/uva_{filename}.cpp")
                else:
                    print("未找到符合規律的程式碼！")
            else:
                print("未找到 <pre class='prettyprint'> 標籤！")
        else:
            print(f"請求失敗，狀態碼: {code_response.status_code}")

    # 下載測資
    for row in soup.find_all('tr')[1:]:
        cols = row.find_all('td')
        question_number = sanitize_filename(cols[0].text)
        question_title = sanitize_filename(cols[1].text)
        code_link = urljoin(url, cols[1].find('a')['href'])
        # 修改下載測資的儲存路徑
        download_and_save(code_link, f'{question_number}_{question_title}_code', folder=test_folder)

if __name__ == "__main__":
    main()


"""
Date:
2024-10-15
2024-05-21
2024-04-23
2023-12-12
2023-10-17
2023-05-23
2023-03-21
2022-12-13
2022-10-18
2022-05-24
2022-03-22
2021-12-21
2021-10-19
2021-05-25
2021-03-23
2020-10-20
2020-06-09
2020-05-26
2019-12-17
2019-09-24
2019-05-28
2019-03-26
2018-12-18
2018-10-02
2018-05-29
2018-03-27
2017-12-19
2017-09-26
2017-05-23
2017-03-28
2016-12-20
2016-10-04
2016-05-24
2016-03-22
2015-12-22
2015-10-06
2015-05-26
2015-03-24
2014-12-23
2014-09-23
2014-05-27
2014-03-25
2013-12-17
2013-10-01
2013-05-28
2013-03-26
2012-12-18
2012-09-25
2012-05-29
2012-03-27
2011-12-20
2011-09-27
2011-05-25
"""