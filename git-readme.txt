the regular procudre should be:
(https://git-lfs.com/)
on c4dynamics: 
git lfs install
git lfs track "*.data-00000-of-00001,*.weights"
git add .gitattributes
git add *.data-00000-of-00001,*.weights
git commit -m "yolo weights throuhg lfs"
git push origin main


but i had probably done some mistake because when i pushed the files nothing helped.
then i did this: 
(https://github.com/git-lfs/git-lfs/blob/main/docs/man/git-lfs-migrate.adoc?utm_source=gitlfs_site&utm_medium=doc_man_migrate_link&utm_campaign=gitlfs#migrate-unpushed-commits)
git lfs migrate info (just watch large files)
git lfs mirgrate import --include="*.data-00000-of-00001,*.weights"
override changes? y.
git push origin main (or github desktop push)
working perfectly. 
