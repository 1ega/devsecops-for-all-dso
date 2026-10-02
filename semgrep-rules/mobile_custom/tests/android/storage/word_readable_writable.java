    int perms = FileUtils.S_IRUSR | FileUtils.S_IWUSR
            | FileUtils.S_IRGRP | FileUtils.S_IWGRP;
    // ruleid:android.mobsf.world_readable
    if ((mode & Context.MODE_WORLD_READABLE) != 0) {
        perms |= FileUtils.S_IROTH;
    }
    // ruleid:android.mobsf.world_writeable
    if ((mode & Context.MODE_WORLD_WRITEABLE) != 0) {
        perms |= FileUtils.S_IWOTH;
    }
    FileUtils.setPermissions(name, perms, -1, -1);