-- Создание таблицы для трейсинга в ClickHouse
CREATE TABLE IF NOT EXISTS traces (
    trace_id UUID,
    service_name String,
    timestamp DateTime,
    request_path String,
    method String,
    status_code UInt16,
    duration_ms UInt32
) ENGINE = MergeTree()
ORDER BY (trace_id, timestamp);

    -- Удаление существующих таблиц
    DROP TABLE IF EXISTS order_items CASCADE;
    DROP TABLE IF EXISTS orders CASCADE;
    DROP TABLE IF EXISTS products CASCADE;
    DROP TABLE IF EXISTS manufacturers CASCADE;
    DROP TABLE IF EXISTS users CASCADE;
    DROP TABLE IF EXISTS reviews CASCADE;
   	DROP TABLE IF EXISTS categories CASCADE;


    -- Создание новых таблиц
    
        -- Тип для прав пользователей
    CREATE TYPE user_role AS ENUM ('user', 'admin');
    
    -- Таблица пользователей (users) с объединенными данными пользователей и админов
    CREATE TABLE users (
        user_id SERIAL PRIMARY KEY,
        password TEXT NOT NULL,
        email VARCHAR(255) UNIQUE NOT NULL,
        balance FLOAT DEFAULT 0,
        role user_role NOT NULL DEFAULT 'user'
    );
    
    -- Таблица производителей (manufacturers)
    CREATE TABLE manufacturers (
        manufacturer_id SERIAL PRIMARY KEY,
        name VARCHAR(255) UNIQUE NOT NULL,
        country VARCHAR(100) NOT NULL
    );
   
      -- Создание таблицы categories
    CREATE TABLE categories (
        category_id SERIAL PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        description TEXT 
    );
    
    -- Таблица продуктов (products), объединенная с products_info
    CREATE TABLE products (
        product_id SERIAL PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        price FLOAT NOT NULL,
        stock INT NOT NULL,
        description TEXT,
        warranty_period INT, -- Гарантийный период в месяцах
        manufacturer_id INT REFERENCES manufacturers(manufacturer_id) ON DELETE SET NULL,
        category_id INT REFERENCES categories(category_id) ON DELETE SET NULL

    );

    -- Таблица заказов (orders)
    CREATE TABLE orders (
        order_id SERIAL PRIMARY KEY,
        user_id INT REFERENCES users(user_id) ON DELETE CASCADE,
        total_price FLOAT NOT NULL,
        order_date TIMESTAMP NOT NULL,
        status VARCHAR(50) NOT NULL
    );

    -- Таблица отзывов (reviews)
    CREATE TABLE reviews (
        review_id SERIAL PRIMARY KEY,
        product_id INT REFERENCES products(product_id) ON DELETE CASCADE,
        user_id INT REFERENCES users(user_id) ON DELETE CASCADE,
        rating INT CHECK (rating >= 1 AND rating <= 5),
        review_text TEXT,
        review_date DATE NOT NULL
    );  
    
    -- Таблица с товарами в заказе
    CREATE TABLE order_items (
        order_item_id SERIAL PRIMARY KEY,
        order_id INT REFERENCES orders(order_id),
        product_id INT REFERENCES products(product_id),
        quantity INT NOT NULL
        --price DECIMAL NOT NULL
    );
   
   
 
    -- Заполнение таблиц
    
    -- Заполнение таблицы users
    INSERT INTO
        users (password, email, balance, role)
    VALUES
        ('admin', 'admin@admin.com', 150.0, 'admin'),   -- Админ
        ('123', 'lev@lev.com', 200.0, 'user'),
        ('aboba', 'aboba@aboba.com', 100.0, 'user'),
        ('qwerty', 'obama@mypresident.ru', 0.0, 'user');
    
    -- Заполнение таблицы manufacturers
    INSERT INTO
        manufacturers (name, country)
    VALUES
        ('TRIPLE H', 'Russia'),
        ('НИКАКОЙ ТРЯСКИ', 'Toba, Samosir'),
        ('iHerb', 'USA'),
        ('BombBar', 'Russia');
       
        -- Добавление записей в таблицу categories
    INSERT INTO categories (name, description)
    VALUES
        ('Протеины', 'Продукты с высоким содержанием белка, используемые для набора мышечной массы.'),
        ('Витамины', 'Витаминные комплексы для поддержания здоровья.'),
        ('Аминокислоты', 'Препараты для восстановления и улучшения работы мышц.'),
        ('Гейнеры', 'Продукты для набора массы с высоким содержанием калорий.'),
        ('Энергетики', 'Стимуляторы для увеличения энергии и выносливости.');
    
    -- Заполнение таблицы products
    INSERT INTO products (name, price, stock, description, warranty_period, manufacturer_id, category_id)
    VALUES
        ('Протеин 900 г', 34.99, 5, 'МУЛЬТИПРОТЕИН — это белковая матрица, которая содержит в себе сывороточный и казеиновый белок, что позволяет насытить организм аминокислотами сразу после приема и в течении нескольких часов 24 ГРАММА БЕЛКА НА ПОРЦИЮ!', 6, 1, 1),
        ('Креатин 300 г', 19.99, 3, 'Креатин моногидрат - естественным образом содержащийся в мышцах, производит энергию, позволяя вам использовать свой потенциал за счет увеличения мышечной массы, увеличения силы и когнитивных функций', 6, 1, 4),
        ('Минеральный набор', 59.99, 2, 'Стак АРХИважных минералов для любого человека, который заботится о своем здоровье В НАБОР ВХОДЯТ: Цинк-селен (1 банка) Медь-бор (1 банка) Магний (3 банки)', 6, 1, 2),
        ('Гейнер 3 кг', 39.99, 6, 'Тру масс — это белково-углеводная матрица, которая поможет вам добрать суточную норму КБЖУ. Отличительной чертой данного гейнера является то, что он содержит в себе МЕДЛЕННЫЕ углеводы и КАЗЕИНОВЫЙ белок (90% гейнеров на рынке содержат дешевый растительный белок 🗑️)', 6, 1, 4),
        ('BCAA 8:1:1 300 г', 19.99, 3, 'BCAA - комплекс незаменимых аминокислот, а именно: лейцина, изолейцина и валина, которые крайне необходимы для мышечного роста 💪', 6, 1, 3),
        ('Ашваганда 120 капсул', 54.99, 5, 'Ашваганда — растительный адаптоген, способный решить проблемы с высоким кортизолом и низким тестостероном, а также сделает тебя хладнокровным в стрессовых ситуациях. 120 таблеток 1000мг 10%', 6, 1, 2),
        ('L-теанин 60г 🦍', 44.99, 3, 'L-теанин — аминокислота, полученная из листьев зеленого чая, является уникальной, так как не не синтезируется в организме и не содержится в естественных условиях, добывается только из зеленого чая (Camellia sinensis). Абсолютно натуральная добавка из чая. Увеличивает концентрацию внимания и фокус, улучшает кратковременную память, убирает вредные навязчивые мысли, снижает кортизол, повышает интеллектуальные способности и активность головного мозга, способствует уменьшению стресса, чувства тревоги и раздражительности, благоприятно влияет на центральную нервную систему, предотвращает тряску.', 12, 2, 3),
        ('Протеиновый батончик Bombbar - Ассорти (20 шт.)', 19.99, 8, 'Протеиновые батончики с низким содержанием сахара.', 3, 4, 1),
        ('Комплекс витаминов группы В с витамином С и цинком 90шт', 14.99, 2, 'California Gold Nutrition® B Complex Gummies feature several B vitamins in fun and tasty gummies that are naturally strawberry flavored and formulated without artificial colors or sweeteners. ', 24, 3, 2),
        ('Изотонический напиток - Лесные ягоды (500 мл)', 0.99, 5, 'Напиток помогает поддерживать оптимальный уровень сахара в крови, восполняет минеральный баланс, предотвращает судороги и спазмы, повышает выносливость, результативность и силовые показатели, способствует быстрому восстановлению после нагрузок.', 3, 4, 3);
    
    -- Заполнение таблицы orders
    INSERT INTO
        orders (user_id, total_price, order_date, status)
    VALUES
        (1, 195.99, '2024-12-11 12:30:00', 'Pending'),
        (2, 79.99, '2024-12-12 14:00:00', 'Completed'),
        (3, 20.99, '2024-12-13 09:15:00', 'Shipped');
    
    -- Заполнение таблицы reviews
    INSERT INTO
        reviews (product_id, user_id, rating, review_text, review_date)
    VALUES
        (1, 1, 5, 'Беру данный протеин уже не в первый раз, очень нравится 👍. Приятный вкус, хорошо растворяется в шейкере(без комочков). Рекомендую.', '2024-12-02'),
        (2, 2, 4, 'Креатин рабочий. Перед тренировкой был сонный, выпил креатин - бодрость и выносливость так и прёт. За 2 часа силовой трени даже не устал. Единственный минус - это его яркий вкус. Очень противный вкус, даже до тошноты. Если с водой размешать перед употреблением, то идёт хорошо. В общем советую 👍', '2024-12-03'),
        (3, 3, 4, 'Отличный товар. Приятно брать в руки. Покалываний не замечено. Результат надеюсь увидеть через 3-4 недели. ', '2024-12-04'),
        (4, 1, 4, 'Пил по 2 кактеля в день и набрал 3кг за 2 недели, хотел растянуть его, но если взять баночку по больше и пить по 3-4 кактеля можно набрать еще больше', '2024-12-05'),
        (5, 4, 4, 'Бцаа рабочие, растворяются хорошо, восстановление ускоряют. Но, товарищи, пожалуйста, разнообразьте вкусы. Я уже замучался есть 3 вкуса, 2 из которых похожи друг на друга.', '2024-12-06'),
        (6, 4, 5, 'Что я явно почувствовал,это улучшение сна и самого засыпания У меня большая проблема с этим,после двух капсул быстро вырубался.Мне даже мелатонин такого эффекта не дает На более дальней дистанции смогу дать обратку позже,тк пропил только три дня,а щас заказал банку', '2024-12-07'),
        (7, 1, 5, 'Мир не такой уж солнечный и приветливый. Это очень опасное, жесткое место. И если только дашь слабину, он опрокинет с такой силой тебя, что больше уже не встанешь. Ни ты, ни я, никто на свете не бьет так сильно, как ЖИЗНЬ. Совсем не важно, как ты ударишь, а важно, КАКОЙ ДЕРЖИШЬ УДАР, как двигаешься вперед. Будешь идти – ИДИ, если с испугу не свернешь. Только так побеждают! Если знаешь, чего ты стоишь, иди и бери свое, но будь готов удары держать, а не плакаться и говорить: «Я ничего не добился из-за него, из-за нее, из-за кого-то»! Так делают трусы, а ты не трус! Быть этого не может!', '2024-12-05'),
        (7, 1, 5, 'На первый день после ядерного взрыва. Большой индонезийский остров Суматра. На нем озеро Тоба. На озере Тоба остров Самосир. На острове Самосир лютеранская церковь, а напротив неё холм. Палатка будет на этом холме.', '2024-12-08'),
        (8, 3, 4, 'Люблю протеиновые батончики на перекус + кофе с молоком и вечером выручаю когда хочется чего-нибудь вкусненького. Если съесть обычную конфетку, то невозможно как хочется следующую, в батончиках за счет идеального состава сразу приходит насыщение. Мой любимый вкус шоколад-фундук, не покупала продукцию бомбар больше года и вижу изменения, в шоколад-фундук мало какао или что дает темный цвет батончику, он почти бежевый как и печенье шоколадный брауни. Прошу исправить и вернуть прежний состав и ореха ни одного не попалось.', '2024-12-09'),
        (9, 2, 5, 'купила мужу - он вообще не может глотать таблетки или капсулы. Хорошо что появились жевательные витамины-мармеладки для взрослых.', '2024-12-12'),
        (10, 1, 4, 'Интересный вкус, нет ощущения, как у других подобных напитков при питье, что твое горло чем то обволакивает. Ну и кисловат немного, непривычно, не особо пришелся по душе. Было ощущение как будто пью слегка забродивший морс. Но это субъективно.', '2024-12-08'); 
    
    -- Заполнение таблицы order_items
    INSERT INTO order_items (order_id, product_id, quantity)
    VALUES
        (1, 6, 1),
        (1, 7, 1),  
        (1, 1, 1),  
        (1, 2, 1),   
        (1, 4, 1),  
        (1, 10, 1),  
        (2, 4, 1),  
        (2, 5, 1),  
        (2, 8, 1),   
        (3, 8, 1),  
        (3, 10, 1);  
