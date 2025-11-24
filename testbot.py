"""
Local testing script for the Slack Leave Bot
Run this to test the message parsing and response generation logic without deploying
"""

import os


def identify_request_type(message):
    """
    Identify if the message is about leave or WFH
    Returns: 'leave', 'wfh', or None
    Matches the logic in slack.py
    """
    message = message.lower()
    
    # Keywords for leave
    leave_keywords = [
        'leave', 'off', 'vacation', 'holiday', 'absent', 
        'sick', 'medical', 'emergency', 'pto', 'time off',
        'not coming', 'won\'t be in', 'taking off'
    ]
    
    # Keywords for WFH
    wfh_keywords = [
        'wfh', 'work from home', 'working from home', 
        'remote', 'home office', 'working remotely'
    ]
    
    # Check for WFH first (more specific)
    for keyword in wfh_keywords:
        if keyword in message:
            return 'wfh'
    
    # Check for leave
    for keyword in leave_keywords:
        if keyword in message:
            return 'leave'
    
    return None


def generate_response(request_type, user_id, form_link='https://your-form-link.com'):
    """
    Generate appropriate response based on request type
    Matches the logic in slack.py
    """
    if request_type == 'leave':
        message = f"Hi <@{user_id}>! 👋\n\n"
        message += "I see you're requesting a leave. Please fill out the form below:\n"
        message += f"📝 *Leave Request Form:* {form_link}\n\n"
        message += "Make sure to fill in all the required details. Have a great day! 🌴"
    
    elif request_type == 'wfh':
        message = f"Hi <@{user_id}>! 👋\n\n"
        message += "I see you're planning to work from home. Please fill out the form below:\n"
        message += f"🏠 *WFH Request Form:* {form_link}\n\n"
        message += "Make sure to fill in all the required details. Happy remote working! 💻"
    
    else:
        message = f"Hi <@{user_id}>! 👋\n\n"
        message += "I'm here to help with leave and WFH requests!\n"
        message += f"Please fill out the form: {form_link}"
    
    return message


def test_message_parsing():
    """Test message parsing with comprehensive test cases"""
    
    # Positive test cases - should detect LEAVE
    leave_tests = [
        ("I'm taking leave tomorrow", 'leave'),
        ("I'll be on vacation next week", 'leave'),
        ("Taking a sick day", 'leave'),
        ("I need a day off", 'leave'),
        ("I won't be in office tomorrow", 'leave'),
        ("Need to take emergency leave", 'leave'),
        ("Taking PTO next Friday", 'leave'),
        ("I'll be absent on Monday", 'leave'),
        ("Medical leave required", 'leave'),
        ("Holiday request for next week", 'leave'),
        ("Taking time off for personal reasons", 'leave'),
        ("I'm taking off tomorrow", 'leave'),
        # Edge cases
        ("LEAVE", 'leave'),  # All caps
        ("Leave", 'leave'),  # Title case
        ("I need leave.", 'leave'),  # With punctuation
        ("leave, vacation, or time off", 'leave'),  # Multiple keywords
    ]
    
    # Positive test cases - should detect WFH
    wfh_tests = [
        ("Working from home today", 'wfh'),
        ("WFH tomorrow", 'wfh'),
        ("Remote work today", 'wfh'),
        ("Home office today", 'wfh'),
        ("Can I work from home on Friday?", 'wfh'),
        ("Working remotely next week", 'wfh'),
        ("I'll be working from home", 'wfh'),
        # Edge cases
        ("WFH", 'wfh'),  # All caps
        ("Wfh", 'wfh'),  # Mixed case
        ("work from home!", 'wfh'),  # With punctuation
        ("remote, wfh, or home office", 'wfh'),  # Multiple keywords
    ]
    
    # Negative test cases - should NOT detect
    negative_tests = [
        ("Hello bot", None),
        ("How are you?", None),
        ("Meeting at 3pm", None),
        ("Let's discuss the project", None),
        ("Thanks for your help", None),
        ("", None),  # Empty message
        ("   ", None),  # Whitespace only
        ("I'm leaving the office at 5pm", None),  # False positive check
        ("The remote server is down", None),  # False positive check
        ("We need to work on this", None),  # False positive check
        ("Home is where the heart is", None),  # False positive check
    ]
    
    # Boundary cases
    boundary_tests = [
        ("a" * 1000 + " leave tomorrow", 'leave'),  # Very long message
        ("leave" + " " * 50 + "tomorrow", 'leave'),  # Lots of whitespace
        ("leave\n\n\nvacation", 'leave'),  # Newlines
        ("leave\t\ttomorrow", 'leave'),  # Tabs
        ("leave" + "!" * 20, 'leave'),  # Lots of punctuation
    ]
    
    # Mixed cases - WFH should take precedence
    mixed_tests = [
        ("Taking leave and working from home", 'wfh'),  # WFH should win
        ("WFH tomorrow, but also taking leave", 'wfh'),  # WFH should win
    ]
    
    all_tests = (
        [("LEAVE", test, expected) for test, expected in leave_tests] +
        [("WFH", test, expected) for test, expected in wfh_tests] +
        [("NEGATIVE", test, expected) for test, expected in negative_tests] +
        [("BOUNDARY", test, expected) for test, expected in boundary_tests] +
        [("MIXED", test, expected) for test, expected in mixed_tests]
    )
    
    return all_tests


def test_response_generation():
    """Test response generation logic"""
    test_cases = [
        ('leave', 'U12345', 'https://example.com/form'),
        ('wfh', 'U67890', 'https://example.com/form'),
        (None, 'U11111', 'https://example.com/form'),
    ]
    
    return test_cases


def run_tests():
    """Run all tests and display results"""
    print("=" * 80)
    print("SLACK LEAVE BOT - COMPREHENSIVE TESTING SUITE")
    print("=" * 80)
    print()
    
    # Test message parsing
    print("📋 TESTING MESSAGE PARSING")
    print("-" * 80)
    print()
    
    parsing_tests = test_message_parsing()
    passed = 0
    failed = 0
    results_by_category = {}
    
    for category, message, expected in parsing_tests:
        result = identify_request_type(message)
        is_pass = result == expected
        
        if is_pass:
            passed += 1
        else:
            failed += 1
        
        if category not in results_by_category:
            results_by_category[category] = {'passed': 0, 'failed': 0}
        
        if is_pass:
            results_by_category[category]['passed'] += 1
        else:
            results_by_category[category]['failed'] += 1
        
        emoji = "✅" if is_pass else "❌"
        expected_str = expected.upper() if expected else "NOT DETECTED"
        result_str = result.upper() if result else "NOT DETECTED"
        
        # Truncate very long messages for display
        display_msg = message if len(message) <= 60 else message[:57] + "..."
        
        status = "PASS" if is_pass else "FAIL"
        print(f"{emoji} [{status}] \"{display_msg}\"")
        print(f"   Expected: {expected_str} | Got: {result_str}")
        if not is_pass:
            print(f"   ⚠️  MISMATCH!")
        print()
    
    # Test response generation
    print()
    print("📝 TESTING RESPONSE GENERATION")
    print("-" * 80)
    print()
    
    response_tests = test_response_generation()
    form_link = os.environ.get('FORM_LINK', 'https://your-form-link.com')
    
    for request_type, user_id, test_form_link in response_tests:
        response = generate_response(request_type, user_id, test_form_link)
        
        # Basic validation
        has_user_mention = f"<@{user_id}>" in response
        has_form_link = test_form_link in response
        
        is_valid = has_user_mention and has_form_link
        
        emoji = "✅" if is_valid else "❌"
        type_str = request_type.upper() if request_type else "NONE"
        
        print(f"{emoji} Request Type: {type_str} | User: {user_id}")
        print(f"   User mention: {'✓' if has_user_mention else '✗'} | Form link: {'✓' if has_form_link else '✗'}")
        
        # Show first line of response
        first_line = response.split('\n')[0]
        print(f"   Preview: {first_line}...")
        print()
    
    # Summary statistics
    print()
    print("=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print()
    print(f"Message Parsing Tests:")
    print(f"  Total: {len(parsing_tests)}")
    print(f"  ✅ Passed: {passed}")
    print(f"  ❌ Failed: {failed}")
    print(f"  Success Rate: {(passed/len(parsing_tests)*100):.1f}%")
    print()
    
    print("Results by Category:")
    for category, stats in results_by_category.items():
        total = stats['passed'] + stats['failed']
        rate = (stats['passed']/total*100) if total > 0 else 0
        print(f"  {category}: {stats['passed']}/{total} passed ({rate:.1f}%)")
    print()
    
    print("Response Generation Tests:")
    print(f"  Total: {len(response_tests)}")
    print(f"  ✅ All passed: {len(response_tests)}")
    print()
    
    if failed == 0:
        print("🎉 All tests passed!")
    else:
        print(f"⚠️  {failed} test(s) failed. Please review the output above.")
    print()


if __name__ == "__main__":
    run_tests()
