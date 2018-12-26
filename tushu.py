from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://root:mysql@127.0.0.1:3306/booktest22"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = "test"

# 创建数据库连接
db = SQLAlchemy(app)


# 作者表  一
class Author(db.Model):
    __tablename__ = "t_author"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40), unique=True)
    books = db.relationship("Book", backref="author_info")  # 关系属性


# 书籍表  多
class Book(db.Model):
    __tablename__ = "t_book"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40), unique=True)
    author_id = db.Column(db.Integer, db.ForeignKey("t_author.id"))  # 外键

# 首页
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET': # 展示页面

        try:  # 所有的数据库操作必须做`异常处理`

            # 查询所有的作者
            authors = Author.query.all()
        except BaseException as e:
            flash("数据库查询错误")
            return redirect(url_for("index"))

        # 将数据传入模板渲染
        return render_template("book_test.html", authors=authors)

    # POST处理
    author_name = request.form.get("author_name")
    book_name = request.form.get("book_name")

    # 参数校验
    # 当列表中的每个元素都有值(不为0/None/空字符串)时, all()才会返回True
    if not all([author_name, book_name]):
        flash("参数错误")
        return redirect(url_for("index"))

    # 判断该作者是否已存在
    author = Author.query.filter_by(name=author_name).first()

    try:  # 所有的数据库操作必须做`异常处理`
        if author:  # 作者存在, 添加书籍, 让书籍和作者建立关联

            # 创建书籍
            book = Book(name=book_name)
            # 让书籍和作者建立关联
            author.books.append(book)
            # 添加到数据库
            db.session.add(book)
            db.session.commit()

        else:  # 作者不存在, 添加书籍和作者, 让书籍和作者建立关联

            # 创建书籍和作者
            book = Book(name=book_name)
            author = Author(name=author_name)
            # 让书籍和作者建立关联
            author.books.append(book)
            # 添加到数据库
            db.session.add_all([author, book])
            db.session.commit()

    except BaseException as e:
        flash("数据库操作失败")
        # 增删改操作失败, 需要进行回滚
        db.session.rollback()
        return redirect(url_for("index"))

    # 刷新页面
    return redirect(url_for("index"))


# 删除书籍  使用查询字符串方式来传递书籍id
@app.route('/delete_book')
def delete_book():
    # 获取参数
    book_id = request.args.get("id")
    try:
        book_id = int(book_id)
    except BaseException as e:
        flash("参数错误")
        return redirect(url_for("index"))

    # 根据id查询书籍模型
    book = Book.query.get(book_id)
    # 从数据库中删除
    db.session.delete(book)
    db.session.commit()
    # 刷新页面
    return redirect(url_for("index"))


# 删除作者  使用动态URL来传递作者id
@app.route('/delete_author/<int:author_id>')
def delete_author(author_id):
    # 根据id查询作者模型
    author = Author.query.get(author_id)

    # 先删除书籍  删除一对多关系数据, 先删除多, 再删除一
    for book in author.books:
        db.session.delete(book)

    # 再删除作者
    db.session.delete(author)
    db.session.commit()

    # 刷新页面
    return redirect(url_for("index"))




if __name__ == '__main__':
    # 删除数据库
    db.drop_all()
    # 创建数据库
    db.create_all()

    # 生成数据
    au1 = Author(name='老王')
    au2 = Author(name='老尹')
    au3 = Author(name='老刘')
    # 把数据提交给用户会话
    db.session.add_all([au1, au2, au3])
    # 提交会话
    db.session.commit()

    bk1 = Book(name='老王回忆录', author_id=au1.id)
    bk2 = Book(name='我读书少，你别骗我', author_id=au1.id)
    bk3 = Book(name='如何才能让自己更骚', author_id=au2.id)
    bk4 = Book(name='怎样征服美丽少女', author_id=au3.id)
    bk5 = Book(name='如何征服英俊少男', author_id=au3.id)
    # 把数据提交给用户会话
    db.session.add_all([bk1, bk2, bk3, bk4, bk5])
    # 提交会话
    db.session.commit()

    app.run(debug=True)