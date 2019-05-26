import requests
import bs4
import shutil
import xlwt
import os
import datetime


BASE_DIR = os.path.abspath(os.path.dirname(__file__).decode('utf-8'))
MEDIA_ROOT = os.path.join(BASE_DIR, 'media/')

SCRAP_MAIN_URL = 'http://www.agriculture.gov.au/pests-diseases-weeds/plant#identify-pests-diseases'
BASE_URL ="http://www.agriculture.gov.au"

def scrap_data():
        scraped_data  = []
        res = requests.get(SCRAP_MAIN_URL)

        count =0
        images = bs4.BeautifulSoup(res.text,'html').find('ul', class_='flex-container').find_all("li")
        for ul in images[16:]:
            data_list = []
            href = ul.find('a')
            count+=1
            print(count)
            scrap_url = (href['href'])
            try:
                if scrap_url:

                    if str(scrap_url[0:4]) == "http":
                        scrapping_url = str(scrap_url)

                    else:
                        scrapping_url = BASE_URL + str(scrap_url)


                    print(scrapping_url)
                    res = requests.get(scrapping_url)
                    soup =bs4.BeautifulSoup(res.content, 'html.parser')
                    image_src= soup.find('div', {"class": "pest-header-image"})

                    if image_src :
                        image_url = get_img_src_and_save(image_src)
                        if not str(image_url) == "Not Found":
                            data_list.append(image_url)#get image path
                            data_list.append(save_image(image_url))#save image and get append imafe path
                        else:
                            data_list.append(image_url)
                            data_list.append("Not Found")

                    elif soup.find('div', {"class": "alignnone"}):
                        image_url = get_img_src_and_save(soup.find('div', {"class": "alignnone"}))
                        if not str(image_url) == "Not Found":
                            data_list.append(image_url)  # get image path
                            data_list.append(save_image(image_url))  # save image and get append imafe path
                        else:
                            data_list.append(image_url)
                            data_list.append("Not Found")

                    else:
                        data_list.append("Not Found")

                    origin= soup.find('div', {"class": "pest-header-content"})#finding origin parent div

                    if origin and origin.find("strong",text='Origin: '):
                        data_list.append(str(origin.find("strong",text='Origin: ').next_sibling))#getting origin text

                    else:
                        data_list.append("Not Found")

                    pathway = soup.find('div', {"class": "pest-header-content"})#finding pathway parent div

                    if pathway and pathway.find("strong",text='Pathways: '):
                        data_list.append(str(pathway.find("strong",text='Pathways: ').next_sibling))#finding pathway text
                    else:
                        data_list.append("Not Found")

                    scraped_data.append(data_list)
                    print("data append")

            except Exception as e:
                print(e)
                break

        print("GOING TO END")
        return  export_data_xls(['Image','Local image path', 'Origin', 'Pathways'],scraped_data)



def export_data_xls(columns, rows):
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet("scraped_data",cell_overwrite_ok=True)
    row_num = 0
    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)
    font_style = xlwt.XFStyle()

    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            ws.write(row_num, col_num, unicode(row[col_num]), font_style)

    return wb.save("scraped_data.xls")

def get_img_src_and_save(image_src):

    url = str(image_src.img.get('src'))
    if url:
        if  url[0:4] =='http':
            image_url = str(url)
        else:
            image_url = str(BASE_URL + url)

        return image_url
    else:
     image_url = "Not Found"

     return image_url


def save_image(image_url):
    dirname = datetime.datetime.now().strftime('%Y.%m.%d.%H.%M.%S')
    filename = "%s_%s.%s" % ("image", dirname, 'png')
    raw_file_path_and_name = os.path.join(filename)
    response = requests.get(image_url, stream=True)
    with open(MEDIA_ROOT + raw_file_path_and_name, 'wb') as out_file:
        shutil.copyfileobj(response.raw, out_file)
    return str(out_file.name)


