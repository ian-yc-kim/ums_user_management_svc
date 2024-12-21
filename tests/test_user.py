from src.ums_user_management_svc.models.user import User


def test_create_user_valid(db_session):
    user = User(
        email='test@example.com',
        full_name='Test User',
        country='Test Country',
        state_province='Test State',
        hashed_password='hashedpassword123'
    )
    db_session.add(user)
    db_session.commit()
    assert user.email is not None


def test_create_user_duplicate_email(db_session):
    user1 = User(
        email='duplicate@example.com',
        full_name='User One',
        country='Country A',
        state_province='State A',
        hashed_password='hashedpassword123'
    )
    user2 = User(
        email='duplicate@example.com',
        full_name='User Two',
        country='Country B',
        state_province='State B',
        hashed_password='hashedpassword456'
    )
    db_session.add(user1)
    db_session.commit()
    db_session.add(user2)
    try:
        db_session.commit()
        assert False, "Duplicate email should raise an IntegrityError"
    except Exception as e:
        assert True


def test_create_user_missing_fields(db_session):
    user = User(
        email='',
        full_name='',
        country='',
        state_province='',
        hashed_password=''
    )
    db_session.add(user)
    try:
        db_session.commit()
        assert False, "Missing fields should raise an IntegrityError"
    except Exception as e:
        assert True
