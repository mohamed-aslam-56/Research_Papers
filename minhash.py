import heapq
import hashlib
import numpy as np

docs=[
    "Today is Tuesday",
    "Tuesday is today",
    "Lionel Messi plays for Argentina",
    "Lionel Messi playing for Argentina",
    "BluBridge is an AI-based research company",
    "One of the AI-based research companies is BluBridge"
]

num_hashes=40
num_buckets=20
rows_per_bucket=2 # N=b*r
merenne_prime=(1<<61)-1 # 2**61 -1

#Params for the permuatation formula 
gen=np.random.RandomState(1)
p_a=np.random.randint(1,merenne_prime,dtype=np.uint64,size=(num_hashes)).tolist()
p_b=np.random.randint(0,merenne_prime,dtype=np.uint64,size=(num_hashes)).tolist()

def get_signature(text,p_a,p_b):
     
    #Simplify and Tokenize
    words=text.lower().replace('.','').split()

    #Shingling or grams
    shingles=words
    shingles_hashes=[int(hashlib.md5(s.encode()).hexdigest(),16)%merenne_prime for s in shingles]

    sig=[]

    for a_val, b_val in zip(p_a, p_b):
        if not shingles_hashes:
            sig.append(0)
        else:
            # FIX 2: Pure Python math prevents OverflowError
            min_phv = min((h * a_val + b_val) % merenne_prime for h in shingles_hashes)
            sig.append(min_phv)
    return sig

#Creating signatures and simulating bucket files
bucket_files={b:[] for b in range(num_buckets)}

for doc_id,doc in enumerate(docs):
    sig=get_signature(doc,p_a,p_b)
    for b in range(num_buckets):
        start,end=b*rows_per_bucket,b*rows_per_bucket+rows_per_bucket
        bucket_slice=tuple(sig[start:end])
        bucket_files[b].append((bucket_slice,doc_id))
    
for b in bucket_files:
    bucket_files[b].sort()

print("Generated Signatures using Permutation Formula")


duplicate_pairs=set()

for b in range(num_buckets):
    #Signatures are sorted across multiple worker files
    #To combine them and compare duplicates we use priority queue
    pq=[]
    for entry in bucket_files[b]:
        heapq.heappush(pq,entry)

    last_sig,last_id=None,None

    while pq:
        current_sig,current_id=heapq.heappop(pq)
        #If last seen signature matches with the top of heap,te
        if current_sig==last_sig:
            duplicate_pairs.add(tuple(sorted((last_id,current_id))))
            
        last_sig,last_id=current_sig,current_id

print(duplicate_pairs)
print("PriorityQueue based merging completed")

#Union Find Algorithm to find transitive between duplicate pairs
parent={i:i for i in range(len(docs))}

def find(i):
    if(i==parent[i]):return i
    parent[i]=find(parent[i])
    return parent[i]

def union(i,j):
    root_i,root_j=find(i),find(j)
    if root_i!=root_j:parent[root_j]=root_i

for a,b in duplicate_pairs:
    union(a,b)

#the duplicate document tracking
remove_list=[i for i in range(len(docs)) if i!=find(i)]

#Filtering 
final_docs=[doc for i,doc in enumerate(docs) if i not in remove_list]


print("******************FINAL DOCUMENTS*********************   ")
for doc in final_docs:
    print(doc)

