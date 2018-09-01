# -*- coding: utf-8 -*-
from flask_wtf import Form,FlaskForm
from wtforms import StringField,TextAreaField,BooleanField,SelectField,SubmitField
from wtforms.validators import Required,DataRequired, Length, ValidationError
from flask_ckeditor import CKEditorField
from flask_wtf.file import FileField, FileAllowed, FileRequired
from ..models import User,ArticleType
from flask_uploads import UploadSet, IMAGES

icon = UploadSet('photo', IMAGES)
icon1 = UploadSet('headimg', IMAGES)


# 评论输入表单
class CommentForm(Form):
    body = StringField('',validators=[Required()],render_kw={"style":"width:100%;height:100px;"})
    submit = SubmitField(u'提交',render_kw={"style":"float:right;margin-bottom:10px;"})


# 编辑个人资料
class EditProfileForm(FlaskForm):
    username = StringField('昵称')
    name = StringField('真实姓名', validators=[Length(0, 64)])
    location = StringField('居住地', validators=[Length(0, 64)])
    about_me = TextAreaField('个人简介',render_kw={"placeholder": "例如：摄影/潜水爱好者/吃货"})
    submit1 = SubmitField('保存')

    def __init__(self, user, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.user = user

    def validate_username(self, field):
        if field.data != self.user.username and \
                User.query.filter_by(username=field.data).first():
            raise ValidationError('该用户名已被使用！')


# 上传头像
class ImgForm(FlaskForm):
    image = FileField('选择图片',validators=[
         FileRequired(u'你还没有选择图片！'),
        FileAllowed(icon, u'只能上传图片！')])
    submit2 = SubmitField('保存为头像')

# 写游记
class PostForm(FlaskForm):
    title = StringField('', validators=[Length(0, 100)], render_kw={"placeholder": '给你的游记一个小标题'})
    headimg = FileField('设置游记头图', validators=[FileAllowed(icon, u'只能上传图片！')])
    type = SelectField('文章类别', coerce=int)
    city = StringField('旅游城市', validators=[Length(0, 64)])
    body = CKEditorField('', validators=[DataRequired()], render_kw={"placeholder": '这里开始游记正文'})
    submit = SubmitField('提交')

    def __init__(self, *args, **kwargs):
        super(PostForm, self).__init__(*args, **kwargs)
        self.type.choices = [(type1.id, type1.type)
                             for type1 in ArticleType.query.order_by(ArticleType.type).all()]


# 搜索表单模型
class SearchForm(FlaskForm):
    searchCity = StringField('',validators=[Required()])
    submit = SubmitField('搜索')