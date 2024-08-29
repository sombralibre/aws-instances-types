import sys
import csv
import json
import boto3

def get_pricing_data(region, profile_name="default"):
    session = boto3.Session(profile_name=profile_name)
    client = session.client('pricing', region_name=region)

    response = client.get_products(
        ServiceCode='AmazonEC2',
        Filters=[
            {'Type': 'TERM_MATCH', 'Field': 'location', 'Value': region}
        ],
        FormatVersion='aws_v1'
    )

    return response['PriceList']

def parse_pricing_data(data):
    instances = []
    for item in data:
        item_json = json.loads(item)
        product = item_json['product']
        attributes = product['attributes']
        instance_type = attributes.get('instanceType')
        memory = attributes.get('memory')
        vcpus = attributes.get('vcpu')

        ondemand_terms = item_json['terms']['OnDemand']
        ondemand_price = None
        for term in ondemand_terms.values():
            for price_dimension in term['priceDimensions'].values():
                ondemand_price = price_dimension['pricePerUnit']['USD']
                break

        spot_price = "N/A"  # Fetch spot pricing separately if needed
        instances.append([instance_type, memory, vcpus, ondemand_price, spot_price])

    return instances

def save_to_csv(instances, filename="ec2_instances.csv"):
    header = ['Instance Type', 'Memory', 'vCPUs', 'On-Demand Price', 'Spot Price']
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(header)
        writer.writerows(instances)


if __name__ == "__main__":
    region = "us-east-1"
    profile_name = sys.argv[1]
    pricing_data = get_pricing_data(region, profile_name)
    instances = parse_pricing_data(pricing_data)
    #print(sys.argv)
    # Save data to CSV
    save_to_csv(instances)
