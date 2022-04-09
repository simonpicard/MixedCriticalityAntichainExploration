#include <vector>
using std::vector;
#include <iostream>
using std::cout;

inline vector<vector<int>> power_set(const vector<int>& elts) {
    if (elts.empty()) {
        return vector<vector<int>>(1,  // vector contains 1 element which is...
                                   vector<int>());  // ...empty vector of ints
    }

    else {
        vector<vector<int>> smaller =
            power_set(vector<int>(elts.begin() + 1, elts.end()));
        int elt = elts[0];  // in Python elt is a list (of int)
                            //      withElt = []
        vector<vector<int>> withElt;
        //      for s in smaller:
        for (const vector<int>& s : smaller) {
            //          withElt.append(s + elt)
            withElt.push_back(s);
            withElt.back().push_back(elt);
        }
        //      allofthem = smaller + withElt
        vector<vector<int>> allofthem(smaller);
        allofthem.insert(allofthem.end(), withElt.begin(), withElt.end());
        //      return allofthem
        return allofthem;
    }
}