import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.api import call_ai, build_user_message, trim_history
from src.prompts import build_system_prompt

test_questions = [
    "报到需要带什么东西",
    "宿舍怎么分配的",
    "军训什么时候开始",
    "学费怎么缴纳",
    "图书馆开放时间",
    "补卡去哪里办理",
    "转专业流程",
    "如何开在读证明",
    "怎么去学校",
    "食堂在哪",
    "设备报修流程",
    "科研申报流程",
    "调课怎么申请",
    "差旅报销需要什么材料",
    "心理援助热线"
]

def test_stability():
    print("=" * 60)
    print("AI小航 连续问答性能稳定性测试")
    print("=" * 60)
    print()
    
    messages = []
    system_prompt = build_system_prompt("1", "报到需要带什么东西")
    messages.append({"role": "system", "content": system_prompt})
    
    success_count = 0
    fail_count = 0
    total_time = 0
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n【第{i}次提问】{question}")
        
        start_time = time.time()
        
        try:
            user_message = build_user_message(question)
            messages.append({"role": "user", "content": user_message})
            messages = trim_history(messages)
            
            answer, error = call_ai(messages)
            
            elapsed_time = time.time() - start_time
            total_time += elapsed_time
            
            if error:
                print(f"  ❌ 失败：{error}")
                fail_count += 1
            else:
                print(f"  ✅ 成功，耗时：{elapsed_time:.2f}秒")
                print(f"  回答长度：{len(answer)}字")
                messages.append({"role": "assistant", "content": answer})
                success_count += 1
                
        except Exception as e:
            elapsed_time = time.time() - start_time
            print(f"  ❌ 异常：{str(e)}，耗时：{elapsed_time:.2f}秒")
            fail_count += 1
    
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    print(f"总提问次数：{len(test_questions)}")
    print(f"成功次数：{success_count}")
    print(f"失败次数：{fail_count}")
    print(f"成功率：{(success_count / len(test_questions)) * 100:.1f}%")
    print(f"总耗时：{total_time:.2f}秒")
    print(f"平均耗时：{total_time / len(test_questions):.2f}秒/次")
    
    if fail_count == 0:
        print("\n🎉 测试通过！程序运行稳定，无崩溃！")
    else:
        print(f"\n⚠️ 测试未完全通过，{fail_count}次失败")

if __name__ == "__main__":
    test_stability()