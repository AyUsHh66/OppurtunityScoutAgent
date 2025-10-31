#include <unordered_map>
#include<vector>
using namespace std;
void customSort(vector<int> &arr, int n){
    unordered_map<int,int> tens;
    for(int i=0; i<n;i++){
        int num=arr[i];
        int digit=(num/10)%10;
        tens[num]=digit;
    }
    
}
