using System;

class ProductArraySolver
{
// ฟังก์ชันหาผลคูณของ array ยกเว้นตัวเอง
static int[] ProductExceptSelf(int[] numbers)
{
int n = numbers.Length;

    // array สำหรับเก็บคำตอบ
    int[] result = new int[n];

    // step 1: เก็บ prefix product (ซ้าย → ขวา)
    result[0] = 1; // ตัวแรกไม่มีตัวซ้าย
    for (int i = 1; i < n; i++)
    {
        // result[i] = ผลคูณของทุกตัวทางซ้ายของ i
        result[i] = result[i - 1] * numbers[i - 1];
    }

    // step 2: คูณ suffix product (ขวา → ซ้าย)
    int rightProduct = 1; // เก็บผลคูณฝั่งขวา

    for (int i = n - 1; i >= 0; i--)
    {
        // เอาค่าฝั่งซ้าย (result[i]) * ฝั่งขวา
        result[i] = result[i] * rightProduct;

        // อัปเดตผลคูณฝั่งขวา
        rightProduct *= numbers[i];
    }

    return result;
}

static void Main()
{
    int[] numbers = { 1, 2, 3, 4 };

    int[] result = ProductExceptSelf(numbers);

    Console.WriteLine("Result:");
    foreach (int num in result)
    {
        Console.Write(num + " ");
    }
}

}
