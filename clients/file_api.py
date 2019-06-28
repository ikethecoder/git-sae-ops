
import os
import shutil
from shutil import Error
from pathlib import Path

import logging
log = logging.getLogger(__name__)

class FileUtils():

    def copytree(self, src, dst, symlinks=False, ignore=None):

        names = os.listdir(src)
        if ignore is not None:
            ignored_names = ignore(src, names)
        else:
            ignored_names = set()

        if not os.path.isdir(dst):
            os.makedirs(dst)
        errors = []
        for name in names:
            # log.info("FileCopy File: %s" % name)

            if name in ignored_names:
                continue

            if name.endswith(".git"):
                continue

            srcname = os.path.join(src, name)
            dstname = os.path.join(dst, name)
            try:
                if symlinks and os.path.islink(srcname):
                    linkto = os.readlink(srcname)
                    os.symlink(linkto, dstname)
                elif os.path.isdir(srcname):
                    # log.info("Copy directory %s to %s" % (srcname, dstname))
                    self.copytree(srcname, dstname, symlinks, ignore)
                else:
                    # log.info("Copying %s to %s" % (srcname, dstname))
                    shutil.copy2(srcname, dstname)
                # XXX What about devices, sockets etc.?
            except (IOError, os.error) as why:
                errors.append((srcname, dstname, str(why)))
            # catch the Error from the recursive copytree so that we can
            # continue with other files
            except Error as err:
                errors.extend(err.args[0])
        try:
            shutil.copystat(src, dst)
        except OSError as why:
            errors.extend((src, dst, str(why)))
        if errors:
            raise Error(errors)


    # Delete files/directories in target that are not in source
    def sync_deletions(self, source, target, ignored_names=[]):

        for root, dirs, files in os.walk(target + "/"):
            relpath = root[len(target)+1:]
            path = relpath.split(os.sep)
            if (path[0] == '.git'):
                continue

            src_path = "%s/%s" % (source, relpath)
            if (Path(src_path).is_dir() == False):
                tar_path = "%s/%s" % (target, relpath)
                # log.info("Remove %s" % tar_path)
                shutil.rmtree(tar_path)
                continue

            for file in files:
                log.info("%s/%s" % (relpath, file))
                if "%s/%s" % (relpath, file) in ignored_names:
                    # log.info("...skipped")
                    continue

                src_path = "%s/%s/%s" % (source, relpath, file)
                if (Path(src_path).is_file() == False):
                    tar_path = "%s/%s/%s" % (target, relpath, file)
                    # log.info("Remove %s" % tar_path)
                    os.remove(tar_path)
