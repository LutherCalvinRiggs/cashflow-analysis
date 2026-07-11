from services.pii_filter import redact


# ── Account numbers ───────────────────────────────────────────────────────────

def test_redacts_labeled_account_number():
    assert redact("Account Number: 483920173627") == "Account Number: ****3627"

def test_redacts_account_number_with_hash():
    assert redact("Account #483920173627") == "Account #****3627"

def test_redacts_account_num_abbreviation():
    assert redact("Acct No: 123456789") == "Acct No: ****6789"

def test_preserves_last4_of_account():
    result = redact("Account Number: 000012345678")
    assert result.endswith("5678")
    assert "000012345678" not in result

def test_redacts_member_number():
    assert redact("Member Number: 483920173627") == "Member Number: ****3627"

def test_redacts_member_no():
    assert redact("Member No: 123456789") == "Member No: ****6789"

def test_does_not_redact_unlabeled_digit_sequence():
    # Transaction reference IDs should be left alone
    assert redact("CHECK 1001 09/15") == "CHECK 1001 09/15"
    assert redact("ACH 4839201 PAYMENT") == "ACH 4839201 PAYMENT"


# ── Routing numbers ───────────────────────────────────────────────────────────

def test_redacts_labeled_routing_number():
    assert redact("Routing Number: 021000021") == "Routing Number: [ROUTING]"

def test_redacts_transit_number():
    assert redact("Transit Number: 021000021") == "Transit Number: [ROUTING]"

def test_redacts_aba_number():
    assert redact("ABA: 021000021") == "ABA: [ROUTING]"

def test_does_not_redact_unlabeled_9_digit_sequence():
    # A transaction amount or reference that happens to be 9 digits
    assert redact("Ref 123456789") == "Ref 123456789"


# ── Card numbers ──────────────────────────────────────────────────────────────

def test_redacts_card_number_spaces():
    assert redact("4532 0151 1283 0366") == "****0366"

def test_redacts_card_number_dashes():
    assert redact("4532-0151-1283-0366") == "****0366"

def test_preserves_last4_of_card():
    result = redact("Card: 4532 0151 1283 9999")
    assert "9999" in result
    assert "4532" not in result

def test_redacts_card_number_unbroken():
    assert redact("4532015112830366") == "****0366"

def test_redacts_card_number_unbroken_preserves_last4():
    result = redact("Card on file: 4532015112839999")
    assert "9999" in result
    assert "453201511283" not in result


# ── SSNs ──────────────────────────────────────────────────────────────────────

def test_redacts_ssn_dashes():
    assert redact("SSN: 123-45-6789") == "SSN: [REDACTED]"

def test_redacts_ssn_spaces():
    assert redact("123 45 6789") == "[REDACTED]"


# ── Multiple patterns in one block of text ────────────────────────────────────

def test_redacts_realistic_statement_header():
    header = (
        "FIRST NATIONAL BANK\n"
        "Account Number: 483920173627\n"
        "Routing Number: 021000021\n"
        "Statement Period: Jan 1 - Jan 31 2026\n"
    )
    result = redact(header)
    assert "483920173627" not in result
    assert "3627" in result          # last 4 preserved
    assert "021000021" not in result
    assert "[ROUTING]" in result
    assert "Jan 1 - Jan 31 2026" in result  # dates untouched


def test_transaction_rows_untouched():
    transactions = (
        "01/15/2026  WHOLE FOODS #0412        -52.34  1,204.56\n"
        "01/16/2026  NETFLIX.COM              -15.99  1,188.57\n"
        "01/17/2026  ACH DEPOSIT 4839201      500.00  1,688.57\n"
    )
    assert redact(transactions) == transactions
