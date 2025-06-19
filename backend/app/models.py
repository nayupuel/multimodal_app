from . import db

class Customer(db.Model):
    """고객 기본정보 테이블 모델"""
    __tablename__ = 'Customer'
    
    CustomerID = db.Column(db.String(10), primary_key=True, comment='고객 고유 식별자(10000001)')
    Name = db.Column(db.String(50), nullable=False, comment='고객 이름')
    SSN_BusinessRegNo = db.Column(db.String(20), unique=True, comment='개인 고객: 주민등록번호, 법인 고객: 사업자등록번호')
    Contact = db.Column(db.String(20), comment='고객 연락처 (전화번호)')
    CustomerType = db.Column(db.Integer, comment='고객 유형: 개인(1) 또는 법인(2)')
    
    accounts = db.relationship('DepositWithdrawalAccount', backref='customer', lazy=True)

class DepositWithdrawalAccount(db.Model):
    """입출금계좌 테이블 모델"""
    __tablename__ = 'DepositWithdrawalAccount'

    AccountID = db.Column(db.String(10), primary_key=True, comment='입출금 계좌 고유 식별자(10000001)')
    CustomerID = db.Column(db.String(10), db.ForeignKey('Customer.CustomerID'), nullable=False, comment='Customer 테이블의 외래 키')
    AccountNumber = db.Column(db.String(20), unique=True, nullable=False, comment='계좌 번호 (고유)')
    Password = db.Column(db.String(6), comment='계좌 비밀번호 (암호화 고려)')
    AccountStatus = db.Column(db.Integer, comment='계좌 상태: 활성(1) 비활성(9), 해지(0)')
    BalanceCount = db.Column(db.Integer, comment='계좌 잔액')
    DWNotiService = db.Column(db.Integer, comment='입출금 알림 서비스 신청 상태: 신청(1), 해지(0), 없음(9)')

    notification_services = db.relationship('NotificationServiceApplication', backref='account', lazy=True)

class NotificationServiceApplication(db.Model):
    """알리미 서비스 이력 테이블 모델"""
    __tablename__ = 'NotificationServiceApplication'

    ApplicationID = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='알림 서비스 신청 고유 식별자')
    CustomerID = db.Column(db.String(10), db.ForeignKey('Customer.CustomerID'), nullable=False)
    AccountID = db.Column(db.String(10), db.ForeignKey('DepositWithdrawalAccount.AccountID'), nullable=False)
    ApplicationDate = db.Column(db.DateTime, default=db.func.current_timestamp(), comment='신청 일시')
    NotificationChannel = db.Column(db.String(10), nullable=False, comment='알림 채널: SMS(1), Push(2)')
    NotificationRecipientNumber = db.Column(db.String(20), nullable=False, comment='알림 수신 번호')
    ApplicationStatus = db.Column(db.Integer, comment='신청 상태: 신청(1), 변경(2), 해지(0)')
    ShowBalanceYn = db.Column(db.String(1), comment='잔액표시여부(Y,N)')
    AutoTransferReceiveStartTime = db.Column(db.String(20), comment='자동이체 수신 시작시간(예: 오전9시)')
    AutoTransferReceiveEndTime = db.Column(db.String(20), comment='자동이체 수신 종료시간(예: 오후10시)') 