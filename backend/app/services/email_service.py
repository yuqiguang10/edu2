# backend/app/services/email_service.py
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from app.core.config import settings


class EmailService:
    """邮件服务"""
    
    def __init__(self):
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_user = settings.SMTP_USER
        self.smtp_password = settings.SMTP_PASSWORD
        self.smtp_tls = settings.SMTP_TLS
    
    async def send_email(
        self, 
        to_email: str, 
        subject: str, 
        body: str, 
        is_html: bool = False
    ) -> bool:
        """发送邮件"""
        if not all([self.smtp_host, self.smtp_port, self.smtp_user, self.smtp_password]):
            print("邮件服务未配置，跳过发送")
            return False
        
        try:
            # 创建邮件
            msg = MIMEMultipart()
            msg['From'] = self.smtp_user
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # 添加邮件正文
            msg.attach(MIMEText(body, 'html' if is_html else 'plain', 'utf-8'))
            
            # 发送邮件
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                if self.smtp_tls:
                    server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
            
            return True
        except Exception as e:
            print(f"邮件发送失败: {e}")
            return False
    
    async def send_password_reset_email(
        self, 
        to_email: str, 
        username: str, 
        reset_token: str
    ) -> bool:
        """发送密码重置邮件"""
        subject = "K12教育平台 - 密码重置"
        
        # 构建重置链接
        reset_url = f"{settings.FRONTEND_URL}/reset-password?token={reset_token}"
        
        body = f"""
        <html>
        <body>
            <h2>密码重置请求</h2>
            <p>亲爱的 {username}，</p>
            <p>您请求重置K12教育平台的密码。请点击下面的链接来重置您的密码：</p>
            <p><a href="{reset_url}" style="color: #007bff;">重置密码</a></p>
            <p>此链接将在30分钟后过期。</p>
            <p>如果您没有请求重置密码，请忽略此邮件。</p>
            <br>
            <p>K12教育平台团队</p>
        </body>
        </html>
        """
        
        return await self.send_email(to_email, subject, body, is_html=True)
