def run(self):
    while True:
        tasks = self.build_asyncio_tasks()
        results = self.loop.run_until_complete(asyncio.gather(*tasks))
        check_tasks = self.build_check_tasks(results)
        if len(check_tasks) >= 1:
            check_results = self.loop.run_until_complete(asyncio.gather(*check_tasks))
            redis_tasks, save_mysql_tasks, check_other_tasks = self.build_other_insert(check_results,get_db)
            if len(redis_tasks) >= 1:
                self.loop.run_until_complete(asyncio.wait(redis_tasks))
            if len(check_other_tasks) >= 1:
                self.loop.run_until_complete(asyncio.wait(check_other_tasks))
                for result_list in self.all_data_list:
                    if result_list != None:
                        # print('时间：' + str(result["update_time"]) + '国家：' + result["country"])
                        task = self.insert_mysql(result_list, get_db)
                        save_mysql_tasks.append(task)
            if len(save_mysql_tasks) >= 1:
                self.loop.run_until_complete(asyncio.wait(save_mysql_tasks))







    def run(self):
        tasks = []
        while True:
            task = asyncio.ensure_future(self.get_redis_apk())
            tasks.append(task)
            if len(tasks) > 50:
                results = self.loop.run_until_complete(asyncio.gather(*tasks))
                tasks = []
                check_tasks = []
                for result in results:
                    task = asyncio.ensure_future(self.check_app_version(result))
                    check_tasks.append(task)
                if len(check_tasks) >= 1:
                    check_results = self.loop.run_until_complete(asyncio.gather(*check_tasks))
                    redis_tasks = []
                    save_mysql_tasks = []
                    check_other_tasks = []
                    get_db = self.loop.run_until_complete(self.get_mysql_db())
                    for check_result in check_results:
                        try:
                            data_return, analysis_data = check_result
                            if data_return != None:
                                task = asyncio.ensure_future(self.save_redis(data_return))
                                redis_tasks.append(task)
                            if analysis_data != None:
                                task = asyncio.ensure_future(self.insert_mysql(analysis_data, get_db))
                                save_mysql_tasks.append(task)
                            if data_return != None and data_return["is_update"] == 1:
                                task = asyncio.ensure_future(self.check_other_coutry(data_return))
                                check_other_tasks.append(task)
                        except Exception as e:
                            print('错误信息：' + str(e))
                    if len(redis_tasks) >= 1:
                        self.loop.run_until_complete(asyncio.wait(redis_tasks))


                    if len(check_other_tasks) >= 1:
                        self.loop.run_until_complete(asyncio.wait(check_other_tasks))
                        for result_list in self.all_data_list:
                            if result_list != None:
                                # print('时间：' + str(result["update_time"]) + '国家：' + result["country"])
                                task = self.insert_mysql(result_list, get_db)
                                save_mysql_tasks.append(task)

                    if len(save_mysql_tasks) >= 1:
                        self.loop.run_until_complete(asyncio.wait(save_mysql_tasks))
