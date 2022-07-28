# SkillFactory_FPW-47_D7.5_SergeyL

#### Для запуска проекта нам потребуется установить все зависимости из файла 
### "requirements.txt"
#### Далее устанавливаем Docker, если он у вас уже установлен, то в терминале запускаем команду
### docker run -d -p 6379:6379 redis

#### После запускаем команды Celery 

### 1. celery -A NewsPaper worker -l INFO
### 2. celery -A NewsPaper beat -l INFO
### 3. celery -A NewsPaper flower