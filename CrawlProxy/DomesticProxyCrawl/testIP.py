

sql_google = '''
                   insert into {} (category,appsize,contentrating,current_version,description,developer,whatsnew,
                   instalations,last_updatedate,minimum_os_version,name,pkgname,price,reviewers,url) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                   ON DUPLICATE KEY UPDATE appsize=VALUES(appsize),category=VALUES(category),contentrating=VALUES(contentrating),
                   current_version=VALUES(current_version),description=VALUES(description),developer=VALUES(developer),whatsnew=VALUES(whatsnew),
                   instalations=VALUES(instalations),last_updatedate=VALUES(last_updatedate),minimum_os_version=VALUES(minimum_os_version),name=VALUES(name),price=VALUES(price)
                '''.format(cls.table_name_dict[lang])
params = (dict_data['Category'], dict_data['AppSize'],
          dict_data['ContentRating'], dict_data['CurrentVersion'],
          dict_data['Description'], dict_data['Developer'], dict_data['WhatsNew'],
          dict_data['Instalations'], dict_data['LastUpdateDate'],
          dict_data['MinimumOSVersion'],
          dict_data['Name'], dict_data['PkgName'], dict_data['Price'],
          dict_data['Reviewers'], dict_data['url'])