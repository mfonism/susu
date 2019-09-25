from enum import Enum, auto, unique


@unique
class AlertType(Enum):
    CHARGE = auto()
    CREDIT = auto()

    def is_credit(self):
        return self.name is 'CREDIT'

    def is_charge(self):
        return not self.is_credit()


@unique
class AlertStatus(Enum):
    FAILURE = auto()
    SUCCESS = auto()

    def is_success(self):
        return self.name is 'SUCCESS'

    def is_failure(self):
        return not self.is_sucess()


class Alert:
    '''
    An alert of an amount of money on a user's card.
    '''
    @classmethod
    def make_charge_alert(cls, user_pk, amount,
        alert_status=AlertStatus.SUCCESS
        ):
        return cls(user_pk, amount, AlertType.CHARGE, alert_status)

    @classmethod
    def make_credit_alert(cls, user_pk, amount,
        alert_status=AlertStatus.SUCCESS
        ):
        return cls(user_pk, amount, AlertType.CREDIT, alert_status)

    def __init__(self, user_pk, amount, alert_type, alert_status):
        assert isinstance(alert_type, AlertType), '\'alert_type\' argument must be an \'AlertType\' instance!'
        assert isinstance(alert_status, AlertStatus), '\'alert_status\' argument must be an \'AlertStatus\' instance!'
        
        self.user_pk = user_pk
        self.amount = amount
        self.alert_type = alert_type
        self.alert_status = alert_status

    def is_credit(self):
        return self.alert_type.is_credit()

    def is_charge(self):
        return self.alert_type.is_charge()

    def is_success(self):
        return self.alert_status.is_success()

    def is_failure(self):
        return self.alert_status.is_failure()
