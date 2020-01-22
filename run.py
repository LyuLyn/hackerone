import shutil
import os
import time
from foxmail import Foxmail


def backup(backup_foldername, files_to_backup):
    current_time = time.strftime("%Y-%m-%d %H.%M.%S", time.localtime())
    backfolder_current = "%s/%s" % (backup_foldername, current_time)
    if not os.path.isdir(backup_foldername):
        os.mkdir(backup_foldername)
    os.mkdir("%s/%s" % (backup_foldername, current_time))
    for file in files_to_backup:
        if os.path.isfile(file):
            shutil.copy(file, backfolder_current)
            current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            print("%s [JOEYLYU] File %s backup DONE!" % (current_time, file))


def remove(files):
    for file in files:
        if os.path.isfile(file):
            os.remove(file)
            current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            print("%s [JOEYLYU] File %s cleaned!" % (current_time, file))


def notifyme(foxmail_addr, pwd, subject, content, attachments, receivers):
    fm = Foxmail(foxmail_addr, pwd)
    fm.set_msg(subject, content)
    fm.set_attachments(attachments)
    fm.set_receivers(receivers)
    fm.send()


if __name__ == "__main__":

    program_list_file = "program_list.json"
    program_list_log_file = "program_list_log.json"
    program_info_file = "program_info.json"
    program_info_log_file = "program_info_log.json"
    hacker_info_file = "hacker_info.json"
    hacker_info_log_file = "hacker_info_log.json"
    backup_foldername = 'crawled data backup'

    files_to_backup = [
        program_list_file, program_list_log_file, program_info_file,
        program_info_log_file, hacker_info_file, hacker_info_log_file
    ]

    run_py_folder = os.path.dirname(os.path.realpath(__file__))
    scrapy_root_folder = run_py_folder
    os.chdir(scrapy_root_folder)

    # remove(files_to_backup)

    command_crawl_program_list = "scrapy crawl program_list -o %s" % program_list_file
    command_crawl_program_info = "scrapy crawl program_info -o %s" % program_info_file
    command_crawl_hacker_info = "scrapy crawl hacker_info -o %s" % hacker_info_file

    os.system(command_crawl_program_list)
    current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    print("%s [JOEYLYU] %s DONE!" % (current_time, "Program list crawled"))

    os.system(command_crawl_program_info)
    current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    print("%s [JOEYLYU] %s DONE!" % (current_time, "Program info crawled"))

    os.system(command_crawl_hacker_info)
    current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    print("%s [JOEYLYU] %s DONE!" % (current_time, "Hacker info crawled"))

    backup(backup_foldername, files_to_backup)

    foxmail_addr = 'lvliangxiong@foxmail.com'
    # QQ authorization code
    passWord = 'xyjzjnlulvxqbbfi'
    msg_subject = 'Hackerone crawling finished'
    msg_content = 'See attachments!'
    msg_attachments = files_to_backup
    msg_receivers = [foxmail_addr, "evelynliyuni@outlook.com"]
    notifyme(foxmail_addr, passWord, msg_subject, msg_content, msg_attachments,
             msg_receivers)
