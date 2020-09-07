import requests,re,sys,io
from datetime import datetime,timedelta
from requests.adapters import HTTPAdapter


next_update = (datetime.today()+timedelta(days=20)).strftime('%Y-%m-%d 02:00:00')

channels = ['Discovery Central Europe|DCENENG-UTC','Animal Planet Europe|APEUENG-UTC','Discovery Showcase HD|HDEUENG-UTC'
            ,'Discovery Science Europe|SCEUENG-UTC']

with io.open("/etc/epgimport/discovery.xml","w",encoding='UTF-8')as f:
    f.write(('<?xml version="1.0" encoding="UTF-8"?>'+"\n"+'<tv generator-info-name="By ZR1">').decode('utf-8'))

for x in channels:
    with io.open("/etc/epgimport/discovery.xml","a",encoding='UTF-8')as f:
        f.write(("\n"+'  <channel id="'+x.split('|')[0]+'">'+"\n"+'    <display-name lang="en">'+x.split('|')[0]+'</display-name>'+"\n"+'  </channel>\r').decode('utf-8')) 

def discovery():
    with requests.Session() as s:
        s.mount('http://', HTTPAdapter(max_retries=10))
        for ch in channels:
            url = s.get('https://exports.pawa.tv/discovery/europe/'+ch.split('|')[1]+'.xml')

            titles = re.findall(r'<BROADCAST_TITLE>(.*?)</BROADCAST_TITLE>',url.text)
            date_start = re.findall(r'<BROADCAST_START_DATETIME>(.*?)</BROADCAST_START_DATETIME>',url.text)
            date_end = re.findall(r'<BROADCAST_END_TIME>(.*?)</BROADCAST_END_TIME>',url.text)
            description = re.findall(r'<TEXT_TEXT>(.*?)</TEXT_TEXT>',url.text)

            for title,start,end,des in zip(titles,date_start,date_end,description):
                if end <=next_update:
                    last_date = end
                    prog_start = datetime.strptime(start,'%Y-%m-%d %H:%M').strftime('%Y%m%d%H%M%S')
                    prog_end = datetime.strptime(end,'%Y-%m-%d %H:%M').strftime('%Y%m%d%H%M%S')
                    epg=''
                    epg+=2 * ' ' + '<programme start="' + prog_start + ' +0000" stop="' + prog_end + ' +0000" channel="'+ch.split('|')[0]+'">\n'
                    epg+=4*' '+'<title lang="en">'+title.replace('&','and').replace('amp;','')+'</title>\n'
                    epg+=4*' '+'<desc lang="en">'+des.replace('&','and').replace('amp;','').strip()+'</desc>\n  </programme>\r'
                    with io.open("/etc/epgimport/discovery.xml","a",encoding='UTF-8')as f:
                        f.write(epg)
                    
            print(ch.split('|')[0]+' epg ends at '+last_date)
            sys.stdout.flush()
            
if __name__ =='__main__':
    discovery()
    with io.open("/etc/epgimport/discovery.xml", "a",encoding="utf-8") as f:
        f.write(('</tv>').decode('utf-8'))
    import json
    with open('/usr/lib/enigma2/python/Plugins/Extensions/Epg_Plugin/times.json', 'r') as f:
        data = json.load(f)
    for bouquet in data['bouquets']:
        if bouquet["bouquet"]=="discovery":
            bouquet['date']=datetime.today().strftime('%A %d %B %Y at %I:%M %p')
    with open('/usr/lib/enigma2/python/Plugins/Extensions/Epg_Plugin/times.json', 'w') as f:
        json.dump(data, f)