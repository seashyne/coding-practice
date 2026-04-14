using System;
using System.Collections.Generic;

class TwoSumSolver
{
// ฟังก์ชันหา index ของตัวเลข 2 ตัวที่บวกกันได้เท่ากับ target
static int[] FindTwoSum(int[] numbers, int target)
{
// Dictionary เก็บค่า: (ตัวเลข, index)
Dictionary<int, int> map = new Dictionary<int, int>();

    // วนลูปดูทุกตัวใน array
    for (int i = 0; i < numbers.Length; i++)
    {
        // หาค่าที่ต้องการให้มาบวกกับตัวปัจจุบันแล้วได้ target
        int complement = target - numbers[i];

        // ถ้าเคยเจอค่านี้มาก่อนใน map
        if (map.ContainsKey(complement))
        {
            // return index ของค่าที่เจอ + index ปัจจุบัน
            return new int[] { map[complement], i };
        }

        // ถ้ายังไม่เจอ ก็เก็บค่าปัจจุบันลง map
        map[numbers[i]] = i;
    }

    // ถ้าไม่มีคำตอบ
    return new int[] { -1, -1 };
}

static void Main()
{
    int[] numbers = { 2, 7, 11, 15 };
    int target = 9;

    int[] result = FindTwoSum(numbers, target);

    Console.WriteLine("Index: [" + result[0] + ", " + result[1] + "]");
}

}
