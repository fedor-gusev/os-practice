# Отчёт по Заданию №2
## Гусев Фёдор, 11-002

# 3. Файловые системы

## 3.1 Определяем файл-устройство, соответствующее добавленному диску. 
Опция `-l` позволит просмотреть все существующие диски:
```
sudo fdisk -l
```

В результате видим, что `sda` - изначальный диск, уже размеченный и на нём текущая операционная система. `sdb` - только что появившийся диск, без разметки:

```
Disk /dev/sda: 10 GiB, 10737418240 bytes, 20971520 sectors
Disk model: VBOX HARDDISK
Units: sectors of 1 * 512 = 512 bytes
Sector size (logical/physical): 512 bytes / 512 bytes
I/O size (minimum/optimal): 512 bytes / 512 bytes
Disklabel type: gpt
Disk identifier: F3302DED-C7C9-4C2A-878E-0266BDA4A278

Device     Start      End  Sectors Size Type
/dev/sda1   2048     4095     2048   1M BIOS boot
/dev/sda2   4096 20969471 20965376  10G Linux filesystem


Disk /dev/sdb: 10 GiB, 10737418240 bytes, 20971520 sectors
Disk model: VBOX HARDDISK
Units: sectors of 1 * 512 = 512 bytes
Sector size (logical/physical): 512 bytes / 512 bytes
I/O size (minimum/optimal): 512 bytes / 512 bytes
```

## 3.2 Создание таблицы разделов
С диском определились, создадим на нём таблицу разделов GPT:

```
sudo fdisk /dev/sdb
```

Просмотрев помощь, используем команду `-g` для выбора именно GPT:
```
Command (m for help): g
```

Результат - успех:
```
Created a new GPT disklabel (GUID: 1BB028D3-E564-5E47-82A2-ACE2B1FD7BE2).
```

Теперь создадим разделы. Первый размером 4Гб и типом Linux filesystem data, используем команду `n`:

```
Command (m for help): n
Partition number (1-128, default 1): 1
First sector (2048-20971486, default 2048): 2048
Last sector, +/-sectors or +/-size{K,M,G,T,P} (2048-20971486, default 20971486): +4G
```

Можно было в первых двух вопросах просто соглашаться вводом, выбирались бы значения по-умолчанию. Изменить требовалось только размер. В результате получаем:

```
Created a new partition 1 of type 'Linux filesystem' and of size 4 GiB.
```

Аналогичным образом поступаем и со вторым разделом: `n`, `default`, `default`, `+6GB`:

```
Command (m for help): n
Partition number (2-128, default 1): 1
First sector (8390656-20971486, default 2048): 2048
Last sector, +/-sectors or +/-size{K,M,G,T,P} (2048-20971486, default 20971486): +6G
```
Результат:
```
Created a new partition 2 of type 'Linux filesystem' and of size 6 GiB.
```

Осталось только сохраниться командой `w`.

Удостоверимся, что разметка прошла успешно:
```
sudo fdisk -l
```

Вывод (взят только фрагмент, связанный именно с этим диском):

```
Device       Start      End  Sectors Size Type
/dev/sdb1     2048  8390655  8388608   4G Linux filesystem
/dev/sdb2  8390656 20971486 12580831   6G Linux filesystem
```

## 3.3 Форматирование разделов
Теперь форматируем разделы в заданные файловые системы. На первом должна быть ext4:

```
sudo mkfs.ext4 /dev/sdb1
```

Вывод длинный:
```
mke2fs 1.46.5 (30-Dec-2021)
Creating filesystem with 1048576 4k blocks and 262144 inodes
Filesystem UUID: 75ad5174-ad46-42cf-bc77-4faa2b019f7d
Superblock backups stored on blocks:
        32768, 98304, 163840, 229376, 294912, 819200, 884736

Allocating group tables: done
Writing inode tables: done
Creating journal (16384 blocks): done
Writing superblocks and filesystem accounting information: done
```

Второй раздел требуется форматировать в ext2:
```
sudo mkfs.ext2 /dev/sdb2
```

Результат:
```
mke2fs 1.46.5 (30-Dec-2021)
Creating filesystem with 1572603 4k blocks and 393216 inodes
Filesystem UUID: 0f72699e-ce26-4a25-9507-9fa46200649f
Superblock backups stored on blocks:
        32768, 98304, 163840, 229376, 294912, 819200, 884736

Allocating group tables: done
Writing inode tables: done
Writing superblocks and filesystem accounting information: done
```

Разберёмся с выделением зарезервированного для `root` пространства. На первом разделе должно быть 5%.

~~Пять процентов вроде и так значение по умолчанию, но всё равно проделаем операцию явно~~

Ключ `-m` здесь позволяет установить процентное значение резервируемого пространства: 
```
sudo tune2fs -m 5 /dev/sdb1
```
Вывод:
```
tune2fs 1.46.5 (30-Dec-2021)
Setting reserved blocks percentage to 5% (52428 blocks)
```

На втором разделе вообще не должно быть такого зарезервированного пространства:
```
sudo tune2fs -m 0 /dev/sdb2
```

Вывод:
```
tune2fs 1.46.5 (30-Dec-2021)
Setting reserved blocks percentage to 0% (0 blocks)
```

## 3.4 Монтирование
Теперь подготовим точки монтирования. Создадим соответсвующие директории, ключ `p` здесь позволяет создавать и родительский каталог, и дочерний:

```
sudo mkdir /media/docs -p
sudo mkdir /mnt/work -p
```

Монтируем:
```
sudo mount /dev/sdb1 /media/docs
sudo mount /dev/sdb2 /mnt/work
```

Теперь нам нужно, чтобы монтирование происходило автоматически при запуске системы, для этого отредактируем файл `/etc/fstab`:

```
sudo nano /etc/fstab
```

Строка имеет вид `устройство` `точка монтирования` `файловая система` `флаги` `резервное копирование` `проверка`. 

Флаги мы устанавливаем стандартные, резервное копирование и проверку раздела на ошибки отключаем.

Добавим в конец две строки, соотсветствующие нашим разделам:
```
/dev/sdb1       /media/docs     ext4    defaults        0       0
/dev/sdb2       /mnt/work       ext2    defaults        0       0
```

# 4. Пользователи и группы

## 4.1 Создадим необходимые группы пользователей
~~Без комментариев~~

```
sudo groupadd developers
sudo groupadd managers
sudo groupadd writers
```

## 4.2 Создадим требуемых пользователей:
```
sudo useradd woody
sudo useradd buzz
```

И добавим их в соответствующую группу. Опция `-a` позволяет именно добавлять в группы, а не перезаписывать, а `-G` указывает, что дальше последует список дополнительных групп:
```
sudo usermod -a -G developers woody
sudo usermod -a -G developers buzz
```

Точно так же поступаем с менеджерами:
```
sudo useradd potato
sudo useradd slinky
sudo usermod -a -G managers potato
sudo usermod -a -G managers slinky
```

И с писателями:
```
sudo useradd rex
sudo useradd sid
sudo usermod -a -G writers rex
sudo usermod -a -G writers sid
```

# 5. Директории и файлы

## 5.1 Работаем с /media/docs

Создаем директорию `manuals`:
```
sudo mkdir /media/docs/manuals
```

Устанавливаем владельцем пользователя `rex` (по тз):
```
sudo chown rex /media/docs/manuals
```

Устанавливаем группу-владельца `writers`:
```
sudo chgrp writers /media/docs/manuals
```

И устанавливаем права доступа. Для владельца `u=`, группы-владельца `g=` и всех остальных `o=`:
```
sudo chmod u=rwx,g=rws,o=rx /media/docs/manuals
```

Аналогичные команды настройки для директории `reports`:
```
sudo mkdir /media/docs/reports
sudo chown potato /media/docs/reports
sudo chgrp managers /media/docs/reports
sudo chmod u=rwx,g=rws,o= /media/docs/reports
```

И для `todo`:
```
sudo mkdir /media/docs/todo
sudo chown woody /media/docs/todo
sudo chgrp developers /media/docs/todo
sudo chmod u=rwx,g=rx,o=rx /media/docs/todo
```

Проверим правильность выполнения:
```
ls -l /media/docs/
```
Получим положительный результат:
```
total 28
drwx------ 2 root   root       16384 дек 21 17:31 lost+found
drwxrwSr-x 2 rex    writers     4096 дек 21 17:45 manuals
drwxrwS--- 2 potato managers    4096 дек 21 17:52 reports
drwxr-xr-x 2 woody  developers  4096 дек 21 17:53 todo
```

## 5.2 Для директории `/mnt/work` аналогичные настройки:
Для `writers`:
```
sudo mkdir /mnt/work/writers
sudo chown rex /mnt/work/writers
sudo chgrp writers /mnt/work/writers
sudo chmod u=rwx,g=rws,o= /mnt/work/writers
```

Для `managers`:
```
sudo mkdir /mnt/work/managers
sudo chown potato /mnt/work/managers
sudo chgrp managers /mnt/work/managers
sudo chmod u=rwx,g=rws,o= /mnt/work/managers
```

Для `developers`:
```
sudo mkdir /mnt/work/developers
sudo chown woody /mnt/work/developers
sudo chgrp developers /mnt/work/developers
sudo chmod u=rwx,g=rws,o= /mnt/work/developers
```

Снова проверим, всё ли верно:
```
ls -l /mnt/work
```
Да, всё хорошо:
```
total 28
drwxrwS--- 2 woody  developers  4096 дек 21 17:57 developers
drwx------ 2 root   root       16384 дек 21 17:31 lost+found
drwxrwS--- 2 potato managers    4096 дек 21 17:56 managers
drwxrwS--- 2 rex    writers     4096 дек 21 17:55 writers
```

## 5.3 Работаем с `/mnt/work/developers`

Символьная `-s` ссылка `docs`:
```
sudo ln -s /media/docs/manuals /mnt/work/developers/docs
```

И `todo`:
```
sudo ln -s /media/docs/todo /mnt/work/developers/todo
```

Проверим правильность:
```
sudo ls -l /mnt/work/developers/
```
OK:
```
total 0
lrwxrwxrwx 1 root developers 19 дек 21 18:06 docs -> /media/docs/manuals
lrwxrwxrwx 1 root developers 16 дек 21 18:06 todo -> /media/docs/todo
```
