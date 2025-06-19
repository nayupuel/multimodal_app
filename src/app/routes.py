from flask import render_template, request, jsonify, session, Blueprint, redirect, url_for, abort, current_app
from .models import db, Customer, DepositWithdrawalAccount, NotificationServiceApplication
import sqlalchemy

# 'main'이라는 이름의 블루프린트 객체 생성
bp = Blueprint('main', __name__)

# 본인 인증 시도 횟수를 세기 위한 세션 변수 키
AUTH_ATTEMPT_COUNT = 'auth_attempt_count'

@bp.route('/')
def index():
    """메인 화면 - 서비스 선택"""
    session.clear() # 메인 페이지로 오면 세션 초기화
    return render_template('index.html')

@bp.route('/auth', methods=['GET', 'POST'])
def auth():
    """본인 인증 화면 및 처리. 성공 시 계좌 목록으로 이동."""
    if request.method == 'GET':
        session[AUTH_ATTEMPT_COUNT] = session.get(AUTH_ATTEMPT_COUNT, 0)
        return render_template('auth.html', action_title='본인인증')

    # POST 요청 (인증 처리)
    attempts = session.get(AUTH_ATTEMPT_COUNT, 0)
    if attempts >= 3:
        return jsonify({'success': False, 'reason': '인증 시도 횟수(3회)를 초과했습니다.'}), 429

    user_type = request.form.get('userType')
    name = request.form.get('userName')
    birth_date = request.form.get('birthDate')
    account_number = request.form.get('accountNumber')
    password = request.form.get('accountPassword')

    try:
        customer_type_value = 1 if user_type == 'personal' else 2
        account = db.session.query(DepositWithdrawalAccount).join(
            Customer, DepositWithdrawalAccount.CustomerID == Customer.CustomerID
        ).filter(
            Customer.Name == name,
            Customer.CustomerType == customer_type_value,
            Customer.SSN_BusinessRegNo.like(f"{birth_date}%"),
            DepositWithdrawalAccount.AccountNumber == account_number
        ).first()

        if account and account.check_password(password):
            customer = account.customer
            session['user_id'] = customer.CustomerID
            session.pop(AUTH_ATTEMPT_COUNT, None)
            return jsonify({'success': True, 'redirect_url': url_for('main.accounts')})
        else:
            session[AUTH_ATTEMPT_COUNT] = attempts + 1
            return jsonify({
                'success': False, 
                'reason': f'정보가 일치하지 않습니다. (남은 시도: {3 - (attempts + 1)}회)'
            })

    except sqlalchemy.exc.OperationalError as e:
        current_app.logger.error(f"Database connection failed: {e}", exc_info=True)
        return jsonify({'success': False, 'reason': '데이터베이스 연결에 실패했습니다. 관리자에게 문의하세요.'}), 500
    except Exception as e:
        current_app.logger.error(f"Authentication error: {e}", exc_info=True)
        return jsonify({'success': False, 'reason': '알 수 없는 오류가 발생했습니다.'}), 500

@bp.route('/accounts')
def accounts():
    """인증 후, 해당 고객의 모든 계좌 목록과 서비스 가입 상태를 보여준다."""
    if 'user_id' not in session:
        return redirect(url_for('main.index'))

    customer_accounts = DepositWithdrawalAccount.query.filter_by(CustomerID=session['user_id']).all()
    
    accounts_with_status = []
    for account in customer_accounts:
        application = NotificationServiceApplication.query.filter(
            NotificationServiceApplication.AccountID == account.AccountID,
            NotificationServiceApplication.ApplicationStatus.in_([1, 2]) # 1:신청, 2:변경
        ).first()
        status = '가입' if application else '미가입'

        # 잔액을 1,000단위 쉼표가 있는 문자열로 미리 포맷합니다.
        balance_str = "0"
        if account.BalanceCount is not None:
            balance_str = f"{account.BalanceCount:,}"

        accounts_with_status.append({
            'account': account, 
            'status': status,
            'balance_str': balance_str
        })
        
    return render_template('account_list.html', accounts_with_status=accounts_with_status)

@bp.route('/apply/<account_id>', methods=['GET', 'POST'])
def apply(account_id):
    """특정 계좌에 대한 서비스 신청"""
    if 'user_id' not in session:
        return redirect(url_for('main.index'))

    account = DepositWithdrawalAccount.query.filter_by(AccountID=account_id, CustomerID=session['user_id']).first_or_404()

    if request.method == 'POST':
        try:
            new_application = NotificationServiceApplication(
                CustomerID=session['user_id'],
                AccountID=account_id,
                NotificationChannel=request.form.get('channel'),
                NotificationRecipientNumber=request.form.get('phoneNumber'),
                ShowBalanceYn='Y' if request.form.get('show_balance') == 'yes' else 'N',
                AutoTransferReceiveStartTime=request.form.get('start_time') if request.form.get('notify_time') == 'custom' else None,
                AutoTransferReceiveEndTime=request.form.get('end_time') if request.form.get('notify_time') == 'custom' else None,
                ApplicationStatus=1 # 신청
            )
            db.session.add(new_application)
            db.session.commit()
            return jsonify({'success': True, 'message': '서비스가 성공적으로 신청되었습니다.'})
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Apply service error: {e}", exc_info=True)
            return jsonify({'success': False, 'message': '신청 처리 중 오류가 발생했습니다.'}), 500
    
    return render_template('service_apply.html', account=account)

@bp.route('/change/<account_id>', methods=['GET', 'POST'])
def change(account_id):
    """특정 계좌에 대한 서비스 변경"""
    if 'user_id' not in session:
        return redirect(url_for('main.index'))

    account = DepositWithdrawalAccount.query.filter_by(AccountID=account_id, CustomerID=session['user_id']).first_or_404()
    
    application = NotificationServiceApplication.query.filter(
        NotificationServiceApplication.AccountID == account_id,
        NotificationServiceApplication.ApplicationStatus.in_([1, 2])
    ).order_by(NotificationServiceApplication.ApplicationDate.desc()).first()

    if not application:
        abort(404, "변경할 서비스 신청 내역이 없습니다.")

    if request.method == 'POST':
        try:
            application.NotificationChannel = request.form.get('channel')
            application.NotificationRecipientNumber = request.form.get('phoneNumber')
            application.ShowBalanceYn = 'Y' if request.form.get('show_balance') == 'yes' else 'N'
            if request.form.get('notify_time') == 'custom':
                application.AutoTransferReceiveStartTime = request.form.get('start_time')
                application.AutoTransferReceiveEndTime = request.form.get('end_time')
            else:
                application.AutoTransferReceiveStartTime = None
                application.AutoTransferReceiveEndTime = None
            application.ApplicationStatus = 2 # 변경
            db.session.commit()
            return jsonify({'success': True, 'message': '서비스가 성공적으로 변경되었습니다.'})
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Change service error: {e}", exc_info=True)
            return jsonify({'success': False, 'message': '변경 처리 중 오류가 발생했습니다.'}), 500

    return render_template('service_change.html', settings=application, account=account)

@bp.route('/cancel/<account_id>', methods=['GET', 'POST'])
def cancel(account_id):
    """특정 계좌에 대한 서비스 해지"""
    if 'user_id' not in session:
        return redirect(url_for('main.index'))

    account = DepositWithdrawalAccount.query.filter_by(AccountID=account_id, CustomerID=session['user_id']).first_or_404()

    application = NotificationServiceApplication.query.filter(
        NotificationServiceApplication.AccountID == account_id,
        NotificationServiceApplication.ApplicationStatus.in_([1, 2])
    ).order_by(NotificationServiceApplication.ApplicationDate.desc()).first()

    if not application:
        abort(404, "해지할 서비스 신청 내역이 없습니다.")

    if request.method == 'POST':
        try:
            application.ApplicationStatus = 0 # 해지
            application.CancellationDate = db.func.current_timestamp()
            db.session.commit()
            return jsonify({'success': True, 'redirect_url': url_for('main.cancel_complete')})
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Cancel service error: {e}", exc_info=True)
            return jsonify({'success': False, 'message': '해지 처리 중 오류가 발생했습니다.'}), 500
    
    return render_template('service_cancel.html', settings=application, account=account)

@bp.route('/cancel-complete')
def cancel_complete():
    """서비스 해지 완료 페이지"""
    return render_template('service_cancel_complete.html')

@bp.route('/faq')
def faq():
    """FAQ 화면"""
    return render_template('faq.html') 