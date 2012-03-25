#!/usr/bin/python
# -*- coding: utf-8 -*-

""" addons repository generator """

import os
import md5
import re
import zipfile
import shutil


def create_zip(path, relname, archname):

    def zipfolder(path, relname, archive):
        paths = os.listdir(path)
        for p in paths:
            p1 = os.path.join(path, p)
            p2 = os.path.join(relname, p)
            if os.path.isdir(p1):
                zipfolder(p1, p2, archive)
            else:
                archive.write(p1, p2)

    archive = zipfile.ZipFile(archname, "w", zipfile.ZIP_DEFLATED)
    if os.path.isdir(path):
        zipfolder(path, relname, archive)
    else:
        archive.write(path, relname)
    archive.close()


class Generator:
    """
        Generates addons repository with aa new addons.xml file
        from each addons addon.xml file and a new addons.xml.md5 hash file.
        Must be run from the root of the checked-out repo.
        Only handles single depth folder structure.
    """
    def __init__(self, repo_path, addons_path, exclude_dirs=(".svn", ".git")):
        self.repo_path = repo_path
        self.addons_path = addons_path
        self.exclude_dirs = exclude_dirs

        self._generate_addons_file()
        self._generate_md5_file(os.path.join(self.repo_path, "addons.xml"))
        # notify user
        print "Finished updating addons xml and md5 files"

    def _get_addon_xml(self, text):
        re_addon = re.compile("<addon.+</addon>", re.S)
        re_id = re.compile("""<addon[^>]+id=['"]([^'"]+)['"]""", re.S)
        re_version = re.compile("""<addon[^>]+version=['"]([^'"]+)['"]""", re.S)
        try:
            addon = re_addon.findall(text)[0]
            return addon, re_id.findall(addon)[0], re_version.findall(addon)[0]
        except:
            return None, None, None

    def _generate_addons_file(self):
        addons = os.listdir(self.addons_path)
        # final addons text
        addons_xml = u"<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>\n<addons>\n"
        # loop thru and add each addons addon.xml file
        for addon in addons:
            try:
                if (not os.path.isdir(addon) or addon in self.exclude_dirs):
                    continue
                # create path
                _path = os.path.join(addon, "addon.xml")
                addon_xml, addon_id, addon_version = self._get_addon_xml(open(_path, "r").read())
                addons_xml += unicode(addon_xml.rstrip() + "\n\n", "UTF-8")
                self._save_structure(os.path.join(self.addons_path, addon), addon_id, addon_version)
            except Exception, e:
                # missing or poorly formatted addon.xml
                print "Excluding %s for %s" % (_path, e,)
                raise
        # clean and add closing tag
        addons_xml = addons_xml.strip() + u"\n</addons>\n"
        # save file
        self._save_file(addons_xml.encode("UTF-8"), file_name="addons.xml")

    def _generate_md5_file(self, file_path):
        try:
            # create a new md5 hash
            m = md5.new(open(file_path, 'r').read()).hexdigest()
            # save file
            self._save_file(m, file_name="addons.xml.md5")
        except Exception, e:
            # oops
            print "An error occurred creating addons.xml.md5 file!\n%s" % (e,)

    def _save_structure(self, addon_path, addon_id, addon_version):
        addon_dir = os.path.join(self.repo_path, addon_id)
        addon_items = os.listdir(addon_path)
        if not os.path.exists(addon_dir):
            os.makedirs(addon_dir)
        if 'changelog.txt' in addon_items:
            shutil.copy2(os.path.join(addon_path, 'changelog.txt'), os.path.join(addon_dir, 'changelog-{version}.txt'.format(version=addon_version)))
        if 'icon.png' in addon_items:
            shutil.copy2(os.path.join(addon_path, 'icon.png'), os.path.join(addon_dir, 'icon.png'))
        if 'fanart.jpg' in addon_items:
            shutil.copy2(os.path.join(addon_path, 'icon.png'), os.path.join(addon_dir, 'fanart.jpg'))

        addon_zip = "{addon_id}-{version}.zip".format(addon_id=addon_id, version=addon_version)
        zip_path = os.path.join(addon_dir, addon_zip)
        create_zip(addon_path, addon_id, zip_path)

    def _save_file(self, data, file_name):
        try:
            # write data to the file
            open(os.path.join(self.repo_path, file_name), "w").write(data)
        except Exception, e:
            # oops
            print "An error occurred saving %s file!\n%s" % (file_name, e,)


if __name__ == "__main__":
    addons = os.getcwd()
    repo = os.path.join(os.getcwd(), os.sep.join(('..', '..', '..', 'Public', 'repo')))
    # start
    Generator(repo, addons)
