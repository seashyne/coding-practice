#include <iostream>
#include <vector>
#include <cmath>
#include <cstdlib>
#include <ctime>

using namespace std;

// sigmoid ธรรมดา เอาไว้ squash ค่าให้อยู่ 0-1
double sigmoid(double x)
{
    return 1.0 / (1.0 + exp(-x));
}

// derivative ของ sigmoid (ใช้ตอน backprop)
double sigmoidDerivative(double y)
{
    return y * (1.0 - y);
}

// สุ่ม weight ช่วง -1 ถึง 1
double randomWeight()
{
    return ((double)rand() / RAND_MAX) * 2.0 - 1.0;
}

class NeuralNetwork
{
private:
    int inputSize, hiddenSize, outputSize;
    double learningRate;

    vector<vector<double>> weightsInputHidden;
    vector<vector<double>> weightsHiddenOutput;

    vector<double> biasHidden;
    vector<double> biasOutput;

public:
    NeuralNetwork(int inSize, int hidSize, int outSize, double lr)
        : inputSize(inSize), hiddenSize(hidSize), outputSize(outSize), learningRate(lr)
    {
        weightsInputHidden.resize(inputSize, vector<double>(hiddenSize));
        weightsHiddenOutput.resize(hiddenSize, vector<double>(outputSize));
        biasHidden.resize(hiddenSize);
        biasOutput.resize(outputSize);

        // init weight แบบสุ่ม ๆ
        for (int i = 0; i < inputSize; i++)
            for (int j = 0; j < hiddenSize; j++)
                weightsInputHidden[i][j] = randomWeight();

        for (int i = 0; i < hiddenSize; i++)
            for (int j = 0; j < outputSize; j++)
                weightsHiddenOutput[i][j] = randomWeight();

        // init bias
        for (int i = 0; i < hiddenSize; i++)
            biasHidden[i] = randomWeight();

        for (int i = 0; i < outputSize; i++)
            biasOutput[i] = randomWeight();
    }

    // forward pass เอาไว้ predict เฉย ๆ
    vector<double> predict(const vector<double>& inputs)
    {
        vector<double> hidden(hiddenSize);
        vector<double> outputs(outputSize);

        // input -> hidden
        for (int j = 0; j < hiddenSize; j++)
        {
            double sum = biasHidden[j];
            for (int i = 0; i < inputSize; i++)
                sum += inputs[i] * weightsInputHidden[i][j];

            hidden[j] = sigmoid(sum);
        }

        // hidden -> output
        for (int k = 0; k < outputSize; k++)
        {
            double sum = biasOutput[k];
            for (int j = 0; j < hiddenSize; j++)
                sum += hidden[j] * weightsHiddenOutput[j][k];

            outputs[k] = sigmoid(sum);
        }

        return outputs;
    }

    // train 1 รอบ (1 sample)
    void train(const vector<double>& inputs, const vector<double>& targets)
    {
        vector<double> hidden(hiddenSize);
        vector<double> outputs(outputSize);

        // ===== forward =====
        for (int j = 0; j < hiddenSize; j++)
        {
            double sum = biasHidden[j];
            for (int i = 0; i < inputSize; i++)
                sum += inputs[i] * weightsInputHidden[i][j];

            hidden[j] = sigmoid(sum);
        }

        for (int k = 0; k < outputSize; k++)
        {
            double sum = biasOutput[k];
            for (int j = 0; j < hiddenSize; j++)
                sum += hidden[j] * weightsHiddenOutput[j][k];

            outputs[k] = sigmoid(sum);
        }

        // ===== output error =====
        vector<double> outputGradients(outputSize);
        for (int k = 0; k < outputSize; k++)
        {
            double error = targets[k] - outputs[k];
            outputGradients[k] = error * sigmoidDerivative(outputs[k]);
        }

        // ===== hidden error =====
        vector<double> hiddenGradients(hiddenSize);
        for (int j = 0; j < hiddenSize; j++)
        {
            double error = 0.0;
            for (int k = 0; k < outputSize; k++)
                error += outputGradients[k] * weightsHiddenOutput[j][k];

            hiddenGradients[j] = error * sigmoidDerivative(hidden[j]);
        }

        // update hidden -> output
        for (int j = 0; j < hiddenSize; j++)
            for (int k = 0; k < outputSize; k++)
                weightsHiddenOutput[j][k] += learningRate * outputGradients[k] * hidden[j];

        for (int k = 0; k < outputSize; k++)
            biasOutput[k] += learningRate * outputGradients[k];

        // update input -> hidden
        for (int i = 0; i < inputSize; i++)
            for (int j = 0; j < hiddenSize; j++)
                weightsInputHidden[i][j] += learningRate * hiddenGradients[j] * inputs[i];

        for (int j = 0; j < hiddenSize; j++)
            biasHidden[j] += learningRate * hiddenGradients[j];
    }
};

int main()
{
    srand((unsigned)time(0));

    // ทำ NN ง่าย ๆ ไว้ลอง XOR
    NeuralNetwork nn(2, 4, 1, 0.5);

    vector<vector<double>> inputs = {
        {0, 0}, {0, 1}, {1, 0}, {1, 1}
    };

    vector<vector<double>> targets = {
        {0}, {1}, {1}, {0}
    };

    // train ไปเรื่อย ๆ
    for (int epoch = 0; epoch < 10000; epoch++)
    {
        for (int i = 0; i < 4; i++)
            nn.train(inputs[i], targets[i]);
    }

    // ลอง predict ดู
    for (auto& input : inputs)
    {
        vector<double> output = nn.predict(input);
        cout << input[0] << " XOR " << input[1] << " = " << output[0] << endl;
    }

    return 0;
}