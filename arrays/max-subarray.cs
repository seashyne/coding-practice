using System;

class MaxSubarraySolver
{
    // ฟังก์ชันหาผลรวมสูงสุดของ subarray
    static int FindMaxSubarraySum(int[] numbers)
    {
        int maxSum = numbers[0];
        int currentSum = numbers[0];

        for (int i = 1; i < numbers.Length; i++)
        {
            currentSum = Math.Max(numbers[i], currentSum + numbers[i]);
            maxSum = Math.Max(maxSum, currentSum);
        }

        return maxSum;
    }

    static void Main()
    {
        int[] numbers = { -2, 1, -3, 4, -1, 2, 1, -5, 4 };
        int result = FindMaxSubarraySum(numbers);

        Console.WriteLine("ผลรวม subarray สูงสุด: " + result);
    }
}