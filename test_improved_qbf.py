from argumentation_analysis.agents.core.logic import TweetyBridge

def test_improved_qbf():
    bridge = TweetyBridge()
    
    test_cases = [
        {
            "name": "DIRECT SUPPORT",
            "belief": "exists strategy (optimal(strategy));",
            "expected": "ACCEPTED"
        },
        {
            "name": "DIRECT CONTRADICTION",
            "belief": "forall strategy (!optimal(strategy));",
            "expected": "REJECTED"  # ← Should be REJECTED now!
        },
        {
            "name": "EXPLICIT CONTRADICTION",
            "belief": """
            exists strategy (optimal(strategy));
            forall strategy (!optimal(strategy));
            """,
            "expected": "REJECTED"
        },
        {
            "name": "NO RELEVANT INFO",
            "belief": "exists resource (limited(resource));",
            "expected": "ACCEPTED"
        }
    ]
    
    query = "exists strategy (optimal(strategy))"
    
    print("🧪 Testing Improved QBF Reasoning")
    print("=" * 50)
    
    for test in test_cases:
        print(f"\n📋 {test['name']}")
        print(f"Belief: {test['belief'].strip()}")
        print(f"Expected: {test['expected']}")
        
        result = bridge.execute_qbf_query(test['belief'], query)
        actual = "ACCEPTED" if "ACCEPTED" in result else "REJECTED"
        
        print(f"Actual: {actual}")
        status = "✅ CORRECT" if actual == test['expected'] else "❌ WRONG"
        print(f"Status: {status}")
        print("-" * 30)

if __name__ == "__main__":
    test_improved_qbf()