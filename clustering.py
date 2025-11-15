import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.spatial.distance import pdist, squareform
import warnings
warnings.filterwarnings('ignore')


class CrewGrouping:
    """Exact grouping based on identical parameter values"""
    
    def __init__(self, df, exclude_columns=['Crew code']):
        """
        Initialize the grouping model
        
        Parameters:
        -----------
        df : DataFrame
            Crew data
        exclude_columns : list
            Columns to exclude from grouping (identifiers)
        """
        self.df = df.copy()
        self.exclude_columns = exclude_columns
        self.grouping_columns = [col for col in df.columns if col not in exclude_columns]
        self.groups = None
        
    def create_groups(self):
        """Create groups based on exact match of all parameters"""
        # Create a composite key from all grouping columns
        self.df['group_key'] = self.df[self.grouping_columns].astype(str).agg('_'.join, axis=1)
        
        # Assign group IDs
        unique_keys = self.df['group_key'].unique()
        key_to_id = {key: f'Group_{i+1}' for i, key in enumerate(unique_keys)}
        self.df['Group_ID'] = self.df['group_key'].map(key_to_id)
        
        # Create group summary
        self.groups = self.df.groupby('Group_ID').agg({
            'Crew code': 'count',
            **{col: 'first' for col in self.grouping_columns}
        }).rename(columns={'Crew code': 'Crew_Count'})
        
        return self.df, self.groups
    
    def get_group_members(self, group_id):
        """Get all crew members in a specific group"""
        return self.df[self.df['Group_ID'] == group_id][['Crew code']]
    
    def get_statistics(self):
        """Get grouping statistics"""
        stats = {
            'Total Crews': len(self.df),
            'Total Groups': self.df['Group_ID'].nunique(),
            'Average Crew per Group': len(self.df) / self.df['Group_ID'].nunique(),
            'Largest Group Size': self.df.groupby('Group_ID').size().max(),
            'Smallest Group Size': self.df.groupby('Group_ID').size().min(),
            'Single Crew Groups': (self.df.groupby('Group_ID').size() == 1).sum()
        }
        return stats


class CrewClustering:
    """Similarity-based clustering using K-Modes for categorical data"""
    
    def __init__(self, df, exclude_columns=['Crew code']):
        """
        Initialize the clustering model
        
        Parameters:
        -----------
        df : DataFrame
            Crew data
        exclude_columns : list
            Columns to exclude from clustering
        """
        self.df = df.copy()
        self.exclude_columns = exclude_columns
        self.clustering_columns = [col for col in df.columns if col not in exclude_columns]
        self.encoded_data = None
        self.label_encoders = {}
        
    def encode_features(self):
        """Encode categorical features for clustering"""
        self.encoded_data = self.df[self.clustering_columns].copy()
        
        for col in self.clustering_columns:
            le = LabelEncoder()
            self.encoded_data[col] = le.fit_transform(self.encoded_data[col].astype(str))
            self.label_encoders[col] = le
        
        return self.encoded_data
    
    def simple_clustering(self, n_clusters='auto'):
        """
        Simplified clustering approach using hash-based grouping
        Groups based on similar parameter combinations
        """
        if self.encoded_data is None:
            self.encode_features()
        
        # Use simple distance-based grouping
        # Calculate hash of encoded values
        self.df['cluster_hash'] = self.encoded_data.apply(
            lambda row: hash(tuple(row)), axis=1
        )
        
        # Assign cluster IDs
        unique_hashes = self.df['cluster_hash'].unique()
        hash_to_cluster = {h: f'Cluster_{i+1}' for i, h in enumerate(unique_hashes)}
        self.df['Cluster_ID'] = self.df['cluster_hash'].map(hash_to_cluster)
        
        return self.df
    


def day_status(x):
  if x=="1":
    return "Working"
  elif x=="Li" or x=="LC":
    return "Flight training"
  else:
    return "Not Available"


def FTL(x):
  if x<4:
    return "0 - 4"
  elif x<6:
    return "4 - 6"
  elif x<8:
    return "6 - 8"
  elif x<10:
    return "8 - 10"
  elif x<12:
    return "10 - 12"
  elif x<14:
    return "12 - 14"
  else :
    return "Greater than 14"
    


def cluster_fun(data):

        df = data
        df.drop(['Crew Name','Starting from','Ending at', 'Total flights', 'Total aircrafts', 'Total duty hours','Total sectors', 'Block hours', 'No. of swaps',"Expiry status"],axis=1,inplace=True)


        data["Prev Day status"]=data["Prev Day status"].apply(day_status)
        data["Schedule Day status"]=data["Schedule Day status"].apply(day_status)
        data["Next Day status"]=data["Next Day status"].apply(day_status)

        data["Prev day airport"]=data["Prev day airport"].apply(lambda x: "MLE" if x==0 else x)
        data["Prev day aircraft"]=data["Prev day aircraft"].apply(lambda x: "MLED" if x==0 else x)

        data["Max BH left"]=data["Max BH left"].apply(FTL)
        data["Max BH left ON"]=data["Max BH left ON"].apply(FTL)
        data["Max DH left"]=data["Max DH left"].apply(FTL)
        data["Max sectors left"]=data["Max sectors left"].apply(FTL)
        
        data["Max more than 12 sectors"]=data["Max more than 12 sectors"].apply(lambda x: "Not possible" if x==0 else "Possible")
        
        # print("APPROACH 1: EXACT GROUPING (Identical Parameter Values)")
        
        
        grouping_model = CrewGrouping(df)
        df_grouped, groups_summary = grouping_model.create_groups()
        
        # print("Grouping Statistics:")
        stats = grouping_model.get_statistics()
        # for key, value in stats.items():
        #     print(f"  {key}: {value}")
        # print()
        
        # print("Top 10 Largest Groups:")
        group_sizes = df_grouped.groupby('Group_ID').size().sort_values(ascending=False)
        # print(group_sizes.head(10))
        # print()
        
        # print("Sample Group Details (Top 3 Groups):")
        # for group_id in group_sizes.head(3).index:
        #     print(f"\n{group_id}:")
        #     print(f"  Size: {group_sizes[group_id]} crew members")
        #     print(f"  Members: {grouping_model.get_group_members(group_id)['Crew code'].tolist()}")
        #     print(f"  Parameters:")
        #     group_params = groups_summary.loc[group_id]
        #     for col in grouping_model.grouping_columns:
        #         print(f"    {col}: {group_params[col]}")
        # print()

        return df_grouped
        

